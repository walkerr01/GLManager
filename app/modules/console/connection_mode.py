import typing as t
import os

from console import Console, FuncItem, COLOR_NAME
from console.formatter import create_menu_bg, create_line

from app.utilities.logger import logger


class SocksManager:
    path = './scripts/'
    filename = 'socks.py'
    socks_path = os.path.join(path, filename)

    def is_running(self, port: int = 80) -> bool:
        cmd = 'screen -ls | grep %s' % port
        return os.system(cmd) == 0

    def start(self, port: int = 80, mode: str = 'http') -> None:
        cmd = 'screen -mdS socks:%s python3 %s --port %s --%s' % (port, self.socks_path, port, mode)
        return os.system(cmd) == 0

    def stop(self, port: int = 80) -> bool:
        cmd = 'screen -X -S socks:%s quit' % port
        return os.system(cmd) == 0

    def get_running_ports(self) -> t.List[int]:
        cmd = 'screen -ls | grep socks: | awk \'{print $1}\' | awk -F: \'{print $2}\''
        output = os.popen(cmd).read()
        return [int(port) for port in output.split('\n') if port]

    @staticmethod
    def download() -> bool:
        url = 'https://raw.githubusercontent.com/DuTra01/GLPlugins/master/scripts/proxy.py'
        cmd = 'wget -O %s %s' % (SocksManager.socks_path, url)
        return os.system(cmd) == 0


class SocksActions:
    @staticmethod
    def start(mode: str = 'http') -> None:
        print(create_menu_bg('PORTA - ' + mode.upper()))

        while True:
            try:
                port_src = input(COLOR_NAME.YELLOW + 'Porta: ' + COLOR_NAME.RESET)
                port_src = int(port_src)

                if SocksManager().is_running(port_src):
                    logger.error('Porta %s já está em uso' % port_src)
                    continue

                break
            except ValueError:
                logger.error('Porta inválida!')

            except KeyboardInterrupt:
                return

        while True:
            try:
                port_dst = input(COLOR_NAME.YELLOW + 'Porta destino: ' + COLOR_NAME.RESET)
                port_dst = int(port_dst)

                if port_dst == port_src:
                    raise ValueError

                break
            except ValueError:
                logger.error('Porta inválida!')

            except KeyboardInterrupt:
                return

        if not port_src <= 0 or not port_dst <= 0:
            logger.error('Porta inválida!')
            Console.pause()
            return

        manager = SocksManager()

        if manager.is_running(port_src):
            logger.error('Porta %s já está em uso!' % port_src)
            Console.pause()
            return

        if not manager.start(port_src, 'http'):
            logger.error('Falha ao iniciar proxy!')
            Console.pause()
            return

        logger.info('Proxy iniciado com sucesso!')
        Console.pause()

    @staticmethod
    def stop() -> None:
        running_ports = SocksManager().get_running_ports()

        if not running_ports:
            logger.error('Nenhum proxy está em execução!')
            Console.pause()
            return

        print(create_menu_bg('PARAR PROXY', set_pars=False))

        create_line()
        print(SocksActions.create_message_running_ports(running_ports))
        create_line()

        while True:
            try:
                port = input(COLOR_NAME.YELLOW + 'Porta: ' + COLOR_NAME.RESET)
                port = int(port)

                if not SocksManager().is_running(port):
                    logger.error('Porta %s não está em uso!' % port)
                    continue

                break
            except ValueError:
                logger.error('Porta inválida!')

            except KeyboardInterrupt:
                return

        if not SocksManager().stop(port):
            logger.error('Falha ao parar proxy!')
            Console.pause()
            return

        logger.info('Proxy parado com sucesso!')
        Console.pause()

    @staticmethod
    def create_message_running_ports(running_ports: t.List[int]) -> str:
        message = COLOR_NAME.YELLOW + 'Portas em uso: ' + COLOR_NAME.RESET
        message += ', '.join(str(port) for port in running_ports)

        return message


def socks_console_main():
    console = Console('SOCKS Manager')
    console.append_item(FuncItem('ABRIR PORTA HTTP', SocksActions.start, 'http'))
    console.append_item(FuncItem('ABRIR PORTA HTTPS', SocksActions.start, 'https'))
    console.append_item(FuncItem('FECHAR PORTA', SocksActions.stop))
    console.show()