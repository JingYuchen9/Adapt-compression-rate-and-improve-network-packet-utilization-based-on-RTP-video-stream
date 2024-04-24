import time

import cv2
import struct
import socket
import numpy as np


class RtpSocketSend:
    def __init__(self):
        # 设置目标IP地址和端口号
        self.target_ip = '192.168.2.90'
        self.target_port = 12345
        self.sum = 0
        # 创建UDP套接字
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 获取摄像头
        self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 720)  # 解决问题的关键！！！
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        # self.cap.set(6, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        # 定义分片大小
        self.chunk_size = 1460
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("无法接收视频流，退出。")
                break
            self.sum += 1
            # # print("记录", self.sum, "帧时间：", time.time())
            # time1 = time.time()
            # frame_rate = int(1 / (time1 - time2))
            # # 写入数据到文件
            # file.write("当前帧率为: ")
            # file.write(str(frame_rate))
            # file.write('\n')
            # print("当前帧率为", frame_rate)
            # time2 = time1

            # 获取帧图像数据
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]  # 压缩率10 占用带宽500kb以内，压缩率90 占用带宽最高2-3M
            _, encoding = cv2.imencode('.jpg', frame, encode_param)  # 开始压缩 上面使用了JPGE压缩算法

            # 将数据分片
            data_chunks = [encoding.tobytes()[i:i + self.chunk_size] for i in range(0,
                                                                                    len(encoding.tobytes()),
                                                                                    self.chunk_size)]
            package_number = 1
            for chunk in data_chunks:
                # RTP头部信息
                version = 2
                padding = 0
                extension = 0
                cc = 0
                marker = 0
                payload_type = 26  # 26 表示jpeg
                sequence_number = self.sum
                timestamp = 0
                ssrc = package_number
                # 构建RTP头部
                rtp_header = struct.pack('!BBHLL',
                                         (version << 6) | (padding << 5) | (extension << 4) | cc,
                                         (marker << 7) | payload_type,
                                         sequence_number,
                                         timestamp,
                                         ssrc)
                # RTP负载（每个分片数据块）
                payload = chunk

                # 合并RTP头部和负载
                rtp_packet = rtp_header + payload

                # 发送RTP数据包
                self.udp_socket.sendto(rtp_packet, (self.target_ip, self.target_port))
                # print("已发送第", self.sum, "帧的第", sequence_number, "包")
                package_number += 1

        self.close_udp()

    def udp_socket_close(self):
        self.udp_socket.close()

    def close_udp(self):
        self.udp_socket.close()


def main():
    RtpSocketSend()


if __name__ == "__main__":
    main()
