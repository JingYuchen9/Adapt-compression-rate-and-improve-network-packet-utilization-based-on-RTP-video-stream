import cv2
import struct
import socket
import numpy as np
import time
import threading


class RtpSocketSend:
    def __init__(self):
        # 设置目标IP地址和端口号
        self.target_ip = '192.168.31.25'
        self.target_port = 12345

        self.local_ip = '192.168.31.194'
        self.local_port = 12346
        self.sum = 0
        self.total_package = 0

        # 创建UDP套接字
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((self.local_ip, self.local_port))
        self.udp_socket.setblocking(False)
        # 获取摄像头
        self.cap = cv2.VideoCapture('waves.mp4')
        # self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(6, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        # 定义分片大小
        self.chunk_size = 1460
        self.remain_payload = None  

        # TTL
        self.time_dict = dict()

        # frame rate
        self.frame_rate = 0
        # self.filter_output = None

        # 压缩率
        self.JPEG_rate = 50

        self.thread = threading.Thread(target=self.rec)
        self.thread.start()  # 启动子线程

        self.start_time = time.time()

        while True:
            time.sleep(0.01)
            ret, frame = self.cap.read()
            self.sum += 1
            if not ret:
                print("无法接收视频流，退出。")
                break
            # 获取帧图像数据
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.JPEG_rate]  # 压缩率10 占用带宽500kb以内，压缩率90 占用带宽最高2-3M
            _, encoding = cv2.imencode('.jpg', frame, encode_param)  
            buffer_contents = encoding.tobytes()
            # 将数据分片
            if self.remain_payload is not None:
                buffer_contents = self.remain_payload + buffer_contents
            for i in range(0, len(buffer_contents), self.chunk_size):
                chunk = buffer_contents[i:i + self.chunk_size]
                # 如果分片大小够1460，那么正常发送，如果不足1460，则储存不足的部分，在下次循环中读取读取出来与下一帧的前半部分凑1460
                if len(chunk) == self.chunk_size:
                    self.send_package(self.sum, chunk)
                if len(chunk) < self.chunk_size:
                    self.remain_payload = chunk
            # print("发送完第", self.sum, "帧的时间: ", time.time())
            # file.write(str(time.time() - start_time) + "\n")
        # end_time = time.time()
        # print("发送完所有数据的总时间: ", end_time - start_time)
        print("发送的总数据包数: ", self.total_package)
        self.udp_socket_close()

    def udp_socket_close(self):
        self.udp_socket.close()

    def send_package(self, frame_num, payload):
        self.total_package += 1
        version = 2
        padding = 0
        extension = 0
        cc = 0
        marker = 0
        payload_type = 26  # 26 表示jpeg
        sequence_number = frame_num
        timestamp = 0
        ssrc = self.total_package
        # 构建RTP头部
        rtp_header = struct.pack('!BBHLL',
                                 (version << 6) | (padding << 5) | (extension << 4) | cc,
                                 (marker << 7) | payload_type,
                                 sequence_number,
                                 timestamp,
                                 ssrc)
        # 合并RTP头部和负载
        rtp_packet = rtp_header + payload

        # 记录发送时间
        self.time_dict[ssrc] = time.time()

        # 发送RTP数据包
        self.udp_socket.sendto(rtp_packet, (self.target_ip, self.target_port))
        # print("send...")

    def rec(self):
        while True:
            try:
                data, addr = self.udp_socket.recvfrom(1024)
                back_frame_num = int.from_bytes(data, byteorder='big')
                # print("第", back_frame_num, "包的往返时间为", time.time() - self.time_dict[back_frame_num])
                if back_frame_num in self.time_dict:
                    current_time = time.time()
                    # if current_time - self.start_time < 10:
                    #     self.JPEG_rate = 20
                    #     continue
                    frame_delay = current_time - self.time_dict.pop(back_frame_num)
                    print("packete delay = ", frame_delay)
                    if frame_delay <= 0.01:
                        self.JPEG_rate = 90
                    if 0.01 < frame_delay <= 0.02:
                        self.JPEG_rate = 80
                    if 0.02 >= frame_delay > 0.05:
                        self.JPEG_rate = 50
                    if 0.05 > frame_delay > 0.08:
                        self.JPEG_rate = 20
                    if frame_delay >= 0.1:
                        self.JPEG_rate = 10
                    print("compressed rate = ", self.JPEG_rate)
            except socket.error as e:
                pass

def main():
    RtpSocketSend()


if __name__ == "__main__":
    main()
