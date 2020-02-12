import paramiko
import time


TERM_HEIGHT = 24
TERM_WIDTH = 80
TERM_ENCODING = 'big5'


class PTTClient:
    def __init__(self, host):
        self.session = paramiko.SSHClient()
        self.session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.session.connect(host, username='bbs', password='')
        self.session.channel = self.session.invoke_shell(height=TERM_HEIGHT, width=TERM_WIDTH)

    def recv_data(self):
        while not self.session.channel.recv_ready():
            time.sleep(0.01)
        data = ''
        while self.session.channel.recv_ready():
            data += self.session.channel.recv(TERM_HEIGHT * TERM_WIDTH).decode(TERM_ENCODING, 'ignore')
        return data


    def send_data(self, data):
        while not self.session.channel.send_ready():
            time.sleep(0.01)
        self.session.channel.send(data.encode(TERM_ENCODING))
        return


    def login(self, username, password, kickOther=False):
        frame = self.recv_data()
        self.send_data(username+'\r\n')
        frame = self.recv_data()
        self.send_data(password+'\r\n')
        frame = self.recv_data()
        while '密碼正確' not in frame:
            frame += self.recv_data()
            if '密碼不對喔' in frame:
                return False
        frame = self.recv_data()

        if '您想刪除其他重複登入的連線嗎' in frame:
            self.send_data('y\r\n' if kickOther else 'n\r\n')
            frame = self.recv_data()
        if '更新與同步線上使用者及好友名單' in frame:
            frame = self.recv_data()
        if '請按任意鍵繼續' in frame:
            self.send_data('a')
            frame = self.recv_data()
        if '刪除以上錯誤嘗試的記錄' in frame:
            self.send_data('y\r\n')
            frame = self.recv_data()
        if '您有一篇文章尚未完成' in frame:
            self.send_data('q\r\n')
            frame = self.recv_data()
        if '您保存信件數目' in frame and '超出上限' in frame:
            self.send_data('a')
            frame = self.recv_data()
            self.send_data('q')
            frame = self.recv_data()
        return True


    def post(self, board, title, content):
        self.send_data('s')
        frame = self.recv_data()
        self.send_data(board+'\r\n')
        frame = self.recv_data()
        if '動畫播放中' in frame:
            self.send_data('q')
            frame = self.recv_data()
        if '請按任意鍵繼續' in frame:
            self.send_data('q')
            frame = self.recv_data()
        self.send_data('\x10')
        self.send_data('\r\n')
        self.send_data(title+'\r\n')
        for char in content:
            self.send_data(char)
        frame = self.recv_data()
        self.send_data('\x18')
        frame = self.recv_data()
        while '檔案處理' not in frame:
            frame += self.recv_data()
        self.send_data('s\r\n')
        frame = self.recv_data()

        if '簽名檔' in frame:
            self.send_data('0\r\n')
            frame = self.recv_data()
        if '請按任意鍵繼續' in frame:
            self.send_data('a')
            frame = self.recv_data()
        return
