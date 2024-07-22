import os
import sys
import json
import time
import random
import argparse
import requests
from colorama import *
from urllib.parse import parse_qs
from datetime import datetime

merah = Fore.LIGHTRED_EX
kuning = Fore.LIGHTYELLOW_EX
hijau = Fore.LIGHTGREEN_EX
biru = Fore.LIGHTBLUE_EX
putih = Fore.LIGHTWHITE_EX
hitam = Fore.LIGHTBLACK_EX
reset = Style.RESET_ALL
line = putih + "~" * 50


class MasterBotod:
    def __init__(self):
        self.marin_kitagawa = lambda data: {
            key: value[0] for key, value in parse_qs(data).items()
        }
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en,en-US;q=0.9",
            "Content-Type": "application/json",
            "Host": "api-yield-pass.masterprotocol.xyz",
            "Origin": "https://miniapp-social.masterprotocol.xyz",
            "Referer": "https://miniapp-social.masterprotocol.xyz/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; Redmi 4A / 5A Build/QQ3A.200805.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.185 Mobile Safari/537.36",
        }

    def login(self, data):
        parser = self.marin_kitagawa(data)
        user = parser.get("user")
        juser = json.loads(user)
        self.log(f"{hijau}try login as {putih}{juser['first_name']}")
        if parser.get("query_id"):
            data = {
                "webInitdata": {
                    "query_id": parser.get("query_id"),
                    "user": json.loads(user),
                    "auth_date": parser.get("auth_date"),
                    "hash": parser.get("hash"),
                }
            }
        if parser.get("chat_instance"):
            data = {
                "webInitdata": {
                    "user": json.loads(user),
                    "chat_instance": parser.get("chat_instance"),
                    "chat_type": parser.get("chat_type"),
                    "auth_date": parser.get("auth_date"),
                    "hash": parser.get("hash"),
                }
            }
        url = "https://api-yield-pass.masterprotocol.xyz/miniApp/api/v1/auth/signin"
        self.del_auth()
        res = self.http(url, self.headers, json.dumps(data))
        token = res.json().get("token")
        if token is None:
            self.log(f"{merah}failed get token, check http.log !")
            return None

        return token

    def solve_task(self):
        self.log(f"{hijau}try completing {putih}task !")
        all_task_url = (
            "https://api-yield-pass.masterprotocol.xyz/miniApp/api/v1/task/all"
        )
        detail_task_url = "https://api-yield-pass.masterprotocol.xyz/miniApp/api/v1/task/list?protocolId="
        com_task_url = (
            "https://api-yield-pass.masterprotocol.xyz/miniApp/api/v1/task/complete/"
        )
        result = self.http(all_task_url, self.headers)
        if result.status_code != 200:
            self.log(f"{merah}something wrong !, check http.log for more info !")
            return False
        for i in result.json():
            _id = i.get("protocolId")
            self.log(f"{hijau}start task protocol id {putih}{_id}")
            res = self.http(f"{detail_task_url}{_id}", self.headers)
            if res.status_code != 200:
                self.log(f"{merah}something wrong !, check http.log for more info !")
                return
            for x in res.json():
                tid = x.get("id")
                ttitle = x.get("title")
                com = x.get("completed")
                self.log(f"{hijau}task id : {putih}{tid} {hijau}title {putih}{ttitle}")
                if com:
                    self.log(f"{kuning}task already completed !")
                    continue
                res = self.http(f"{com_task_url}{tid}", self.headers, json.dumps({}))
                if res.status_code != 201:
                    self.log(
                        f"{merah}failed complete task, check http.log for more info !"
                    )
                    continue
                self.log(f"{hijau}complete task successfully !")

    def get_balance(self):
        info_url = "https://api-yield-pass.masterprotocol.xyz/miniApp/api/v1/user/info"
        res = self.http(info_url, self.headers)
        if res.status_code != 200:
            self.log(f"something wrong!!!, check http.log for more info !")
            return False

        for i in res.json():
            tot = i.get("totalPoints")
            cot = i.get("category")
            self.log(
                f"{hijau}balance {putih}{format(int(float(tot)),'.8f')} {hijau}{cot}"
            )

    def redeem(self):
        redeem_url = (
            "https://api-yield-pass.masterprotocol.xyz/miniApp/api/v1/referrals/redeem"
        )
        payload = {"code": "77TM3"}
        res = self.http(redeem_url, self.headers, json.dumps(payload))

    def start_game(self):
        energy_url = "https://api-yield-pass.masterprotocol.xyz/miniApp/api/v1/clicker-game/energy"
        start_url = "https://api-yield-pass.masterprotocol.xyz/miniApp/api/v1/clicker-game/start"
        end_url = (
            "https://api-yield-pass.masterprotocol.xyz/miniApp/api/v1/clicker-game/end"
        )
        res = self.http(energy_url, self.headers)
        energy = res.text
        if int(energy) <= 0:
            self.log(f"{merah}not enough energy to play game !")
            return False
        self.log(f"{hijau}total energy : {putih}{energy}")
        for i in range(int(energy)):
            res = self.http(start_url, self.headers, json.dumps({}))
            game_id = res.json().get("gameId")
            if game_id is None:
                self.log(f"{merah}failed get game_id, check http.log !")
                return
            self.countdown(23)
            point = random.randint(self.game_min, self.game_max)
            data = {"gameId": game_id, "score": point}
            res = self.http(end_url, self.headers, json.dumps(data))
            if res.status_code != 201:
                self.log(f"{merah}failed save game, check http.log !")
                return
            reward_point = res.json().get("rewardPoints")
            self.log(f"{hijau}score : {putih}{point}")
            self.log(f"{hijau}reward point : {putih}{reward_point}")
        return True

    def countdown(self, t):
        for i in range(t, 0, -1):
            menit, detik = divmod(i, 60)
            jam, menit = divmod(menit, 60)
            jam = str(jam).zfill(2)
            menit = str(menit).zfill(2)
            detik = str(detik).zfill(2)
            print(f"waiting {jam}:{menit}:{detik} ", flush=True, end="\r")
            time.sleep(1)
        print("                                     ", flush=True, end="\r")

    def log(self, msg):
        now = datetime.now().isoformat(" ").split(".")[0]
        print(f"{hitam}[{now}] {msg}{reset}")

    def set_auth(self, token):
        self.headers["Authorization"] = f"Bearer {token}"

    def del_auth(self):
        if self.headers.get("Authorization"):
            self.headers.pop("Authorization")

    def load_config(self, file):
        config = json.loads(open(file).read())
        self.game_min = config["game_point"]["min"]
        self.game_max = config["game_point"]["max"]
        self.auto_task = config["auto_task"]

    def http(self, url, headers, data=None):
        while True:
            try:
                if data is None:
                    res = requests.get(url, headers=headers, timeout=30)
                    open("http.log", "a", encoding="utf-8").write(f"{res.text}\n")
                    return res
                if data == "":
                    res = requests.post(url, headers=headers, timeout=30)
                    open("http.log", "a", encoding="utf-8").write(f"{res.text}\n")
                    return res

                res = requests.post(url, headers=headers, data=data, timeout=30)
                open("http.log", "a", encoding="utf-8").write(f"{res.text}\n")
                return res
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                self.log(f"{merah}connection error, connection timeout !")
                time.sleep(1)
                continue

    def main(self):
        banner = f"""
    {hijau}Auto Play Game for {biru}Master Social Bot
    
    {hijau}By : {putih}@AkasakaID
        """
        arg = argparse.ArgumentParser()
        arg.add_argument("--marinkitagawa", action="store_true")
        arg.add_argument("--data", default="data.txt")
        arg.add_argument("--config", default="config.json")
        args = arg.parse_args()
        if args.marinkitagawa is False:
            os.system("cls" if os.name == "nt" else "clear")
        print(banner)
        datas = open(args.data).read().splitlines()
        self.load_config(args.config)
        self.log(f"{hijau}total account : {putih}{len(datas)}")
        print(line)
        for no, data in enumerate(datas):
            self.log(
                f"{putih}account number : {hijau}{no + 1}{putih}/{hijau}{len(datas)}"
            )
            token = self.login(data)
            if token is None:
                continue
            self.set_auth(token)
            self.get_balance()
            if self.auto_task:
                self.solve_task()
            if self.start_game():
                self.get_balance()
            print(line)


if __name__ == "__main__":
    try:
        app = MasterBotod()
        app.main()
    except KeyboardInterrupt:
        sys.exit()
