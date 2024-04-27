import socket
import struct
import cv2
import numpy as np


class RtpSocketReceive:
    def __init__(self):
        self.local_ip = '192.168.2.90'
        self.local_port = 12345

        self.total_data_list = []
        self.point_frame = 1

        # 创建UDP套接字
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 绑定套接字
        self.udp_socket.bind((self.local_ip, self.local_port))
        file = open('package_usage_o.txt', 'w')
        while True:
            # 接收RTP数据包
            rtp_packet, sender_address = self.udp_socket.recvfrom(2048)  # 适当设置缓冲区大小
            usage = (len(rtp_packet) / 1472) * 100
            file.write(str(usage) + "\n")
            # 解析RTP头部
            (rqt_cc, rqt_payload_type, rqt_sequence_number, rqt_timestamp, rqt_ssrc) = struct.unpack('!BBHLL',
                                                                                                     rtp_packet[:12])
            # print("收到包的序号 = ", rqt_sequence_number)
            # 获取数据载荷
            payload = self.get_payload(rtp_packet)

            if rqt_sequence_number == self.point_frame:
                self.total_data_list.append(payload)
            elif rqt_sequence_number > self.point_frame:
                combined_bytes = b''.join(self.total_data_list)
                frame_data = cv2.imdecode(np.frombuffer(combined_bytes, np.uint8), cv2.IMREAD_COLOR)
                if frame_data is not None:
                    cv2.imshow('Image', frame_data)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                self.total_data_list = []
                self.point_frame = rqt_sequence_number
                self.total_data_list.append(payload)
        self.close_udp()

            # if rqt_sequence_number == 1:
            #     if len(self.total_data_list) != 0:
            #         combined_bytes = b''.join(self.total_data_list)
            #         self.total_data_list.clear()
            #         self.total_data_list.append(payload)
            #         print("清空全局列表")
            #         frame_data = cv2.imdecode(np.frombuffer(combined_bytes, np.uint8), cv2.IMREAD_COLOR)
            #         if frame_data is not None:
            #             cv2.imshow('Image', frame_data)
            #
            #             if cv2.waitKey(1) & 0xFF == ord('q'):
            #                 break
            #             else:
            #                 continue
            #     # 数据拼接
            #     self.total_data_list.append(payload)
            #     print("列表中payload的个数 = ", len(self.total_data_list))
            # elif rqt_sequence_number > 1:
            #     self.total_data_list.append(payload)
            # else:
            #     print("somethin wrong")

    @staticmethod
    def get_payload(packet):
        payload = packet[12:]
        return payload

    def close_udp(self):
        self.udp_socket.close()


def main():
    RtpSocketReceive()


if __name__ == "__main__":
    main()
