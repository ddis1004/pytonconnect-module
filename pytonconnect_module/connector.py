import asyncio
from datetime import datetime
from pytonconnect._ton_connect import TonConnect
from pytonconnect.exceptions import UserRejectsError
from pytonconnect.storage import FileStorage
import qrcode
from PIL import Image

class WalletConnector:

    def __init__(self, connect_id: int, manifest_url: str):
        """
        TonConnect 기반으로 지갑을 연결하는 클래스
        :param chat_id: chat id
        :param manifest_url: Application manifest_url
        """
        self.storage = FileStorage(f'connection_data-{connect_id}.json')
        self.connector = TonConnect(manifest_url, storage=self.storage)
        self.unsubscribe = self.connector.on_status_change(self.status_changed, self.status_error)

        self.is_connected = False

    def status_changed(self, wallet):
        self.unsubscribe()
        self.is_connected = self.connector.connected
        print('Wallet connected. \t Address : ', self.connector.account.address)

    def status_error(e):
        print('connect_error:', e)

    async def restore_connection(self):
        """이전 연결 상태 복원"""
        self.is_connected = await self.connector.restore_connection()

    async def get_wallets(self):
        """사용 가능한 지갑 목록 가져오기"""
        return [w['name'] for w in self.connector.get_wallets()]

    async def connect_wallet(self, wallet_type: str) -> dict[str, Image.Image] | None: 
        """사용자 지갑 연결 (지갑 선택)"""
        wallet = next((wallet for wallet in self.connector.get_wallets() if wallet['name'] == wallet_type), None)
        if wallet is None:
            return None
        generated_url = await self.connector.connect(wallet)
        qr = qrcode.make(generated_url)
        return {"url": generated_url, "qrcode": qr.get_image()}

    async def disconnect_wallet(self):
        """지갑 연결 해제"""
        await self.connector.disconnect()
        self.is_connected = False

    async def wait_for_connection(self):
        if self.is_connected: 
            return
        await self.connector.wait_for_connection()

    async def send_transaction(self, address: str, amount: str, payload: str | None = None):
        """
        트랜잭션 생성 및 전송
        :param address: 수신자 주소
        :param amount: 송금 금액 (NANO TON 단위)
        :param payload: 페이로드 (Cell Boc base64)
        """
        transaction = {
            'valid_until': int(datetime.now().timestamp()) + 900,
            'messages': [
                {'address': address, 'amount': amount, 'payload': payload}
            ]
        }
        try:
            result = await self.connector.send_transaction(transaction)
            print("Transaction sent!")
            return result
        except UserRejectsError:
            return "Transaction rejected by user"
        except Exception as e:
            return f"Unknown error: {e}"


# 실행 예제 (테스트 코드)
async def main():
    chat_id = 123456  # 예제 사용자 ID 
    manifest_url = "https://raw.githubusercontent.com/XaBbl4/pytonconnect/main/pytonconnect-manifest.json"

    wallet_connector = WalletConnector(chat_id, manifest_url)
    await wallet_connector.restore_connection()

    if wallet_connector.is_connected:
        print("Already connected")
    else:
        wallets = await wallet_connector.get_wallets()

        if wallets:
            connection_data = await wallet_connector.connect_wallet("Tonkeeper")
            if connection_data is not None: 
                print("Conenct using url : ", connection_data['url'])
                await wallet_connector.wait_for_connection()
                return connection_data
            else: 
                print(f"Error while creating connection url.")

    if wallet_connector.is_connected:
        result = await wallet_connector.send_transaction("0:0000000000000000000000000000000000000000000000000000000000000000", "1")
        print("Transaction Result:", result)
    if wallet_connector.is_connected:
        await wallet_connector.disconnect_wallet()
        print("Wallet disconnected")


if __name__ == "__main__":
    asyncio.run(main())

