import socket
import struct
import time

import cv2
import numpy as np
from datetime import datetime
import queue
import threading


class RtpSocketReceive:
    def __init__(self):
        # 初始化套接字
        self.local_ip = '192.168.31.25'
        self.local_port = 12345

        self.target_ip = '192.168.31.194'
        self.target_port = 12346

        # 创建UDP套接字
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.TTL_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # 创建新线程
        self.event = threading.Event()
        self.thread = threading.Thread(target=self.player, args=(self.event, ))
        self.thread.start()  # 启动子线程

        # 绑定套接字
        self.udp_socket.bind((self.local_ip, self.local_port))

        # 设置分割字符
        self.target_bytes = b"\xff\xd9"

        # 播放结构
        self.total_data_list = []

        # 处理结构
        self.packet_dict = dict()

        # 创建缓存数据结构
        self.my_queue = queue.Queue()
        file = open('package_total.txt', 'w')
        self.sum = 0
        # self.point_frame_num = 1

        self.frame_rate = 0
        self.start_time = time.time()
        while True:

            # 接收RTP数据包
            rtp_packet, sender_address = self.udp_socket.recvfrom(1472)  # 适当设置缓冲区大小
            usage = (len(rtp_packet) / 1472) * 100
            # file.write(str(usage) + "\n")

            # 解析RTP头部
            (rqt_cc, rqt_payload_type, rqt_sequence_number, rqt_timestamp, rqt_ssrc) = struct.unpack('!BBHLL',
                                                                                                     rtp_packet[:12])
            self.sum += 1

            # print("丢包率 = ", (rqt_ssrc - self.sum) / rqt_ssrc)
            # file.write(str((rqt_ssrc - self.sum) / rqt_ssrc) + "\n")
            print("数据包总数 =", rqt_ssrc)
            file.write(str(rqt_ssrc)+"\n")

            # 返回确认信息计算TTL
            # if rqt_sequence_number > self.point_frame_num:
            #     self.TTL_socket.sendto(self.point_frame_num.to_bytes(2, byteorder='big'), (self.target_ip, self.target_port))
            #     self.point_frame_num = rqt_sequence_number
            self.TTL_socket.sendto(rqt_ssrc.to_bytes(4, byteorder='big'), (self.target_ip, self.target_port))

            # 获取数据载荷
            payload = self.get_payload(rtp_packet)

            # 字典排序
            # 将收到的数据放入字典,若字典中元素个数超过100,则对这个包含了100个数据的字典进行排序,排序过程中会生成一个新的字典,从有序的字典中提取值并推入队列
            self.packet_dict[rqt_ssrc] = payload
            if len(self.packet_dict) >= 100:
                packet_dict_sorted = self.sort_dict_by_keys(self.packet_dict)
                for value in packet_dict_sorted.values():
                    self.my_queue.put(value)
                self.packet_dict.clear()
                self.event.set()
            # print("缓存大小 = ", self.my_queue.qsize())
            # if (time.time() - self.start_time >= 300) or 0xFF == ord('q'):
            #     print("停止接收!!")
            #     break
            if 0xFF == ord('q'):
                print("终止视频播放！！！")
                break
        self.close_udp()

    @staticmethod
    def get_payload(packet):
        payload = packet[12:]
        return payload

    def close_udp(self):
        self.udp_socket.close()

    # 读取收到payload，搜索是否包含b"\xff\xd9" 如果包含，则将前面所有的值存入，前一帧后面的值存入后一帧
    def find_bytes_from_payload(self, payload):
        index = payload.find(self.target_bytes)
        return index

    @staticmethod
    def sort_dict_by_keys(input_dict):
        # 使用 sorted 函数按照字典键进行排序
        sorted_items = sorted(input_dict.items())

        # 使用 collections 模块的 OrderedDict 类构建有序字典
        sorted_dict = dict(sorted_items)

        return sorted_dict

    # 对于子线程, 当队列中有数据的时候会解除wait状态,从队列中获取已经排好序的数据,并查找分隔符,将数据分割完成播放
    def player(self, event):
        print("子线程开始运行")
        event.wait()
        while True:
            payload = self.my_queue.get()
            index = self.find_bytes_from_payload(payload)
            if index >= 0:
                # 前一半放到前一帧的list里面然后序列化 解压 播
                self.total_data_list.append(payload[:index + len(self.target_bytes)])
                combined_bytes = b''.join(self.total_data_list)
                frame_data = cv2.imdecode(np.frombuffer(combined_bytes, np.uint8), cv2.IMREAD_COLOR)
                self.total_data_list.clear()
                if frame_data is not None:
                    cv2.imshow('Image', frame_data)
                    # current_time = time.time()
                    # print("当前帧率为: ", 1 / (current_time - self.frame_rate))
                    # self.frame_rate = current_time
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        print("终止视频播放！！！")
                        break
                if frame_data is None:
                    print("发生丢包!!")
                # 后面要处理另一半
                self.total_data_list.append(payload[index + len(self.target_bytes):])
            if index < 0:
                self.total_data_list.append(payload)


def main():
    RtpSocketReceive()


if __name__ == "__main__":
    main()
