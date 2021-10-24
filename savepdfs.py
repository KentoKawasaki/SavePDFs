# -*- coding: utf-8 -*-
# 必要なライブラリ、モジュールをインポート

import os
import re
import sys
import time

import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup


class SavePDFs:

    """ 初期化 """
    def __init__(self):

        # base_url : 取得したいデータが存在するWebページのURL
        self.base_url = input('URLを入力してください。 > ')

        # # "EXIT"入力によるプログラム終了
        # if base_url == 'EXIT':
        #     sys.exit()

        for i in range(5):
            try: 
                self.dir_name = input('データを保存するディレクトリ名を指定してください > ')
                os.makedirs(self.dir_name) # 保存用のディレクトリを作成

            except FileExistsError as e:
                print(e, ': 指定したディレクトリは既に存在しています')
                if i == 4:
                    print('指定回数が上限に達したので、プログラムを終了します')
                    sys.exit()
            else:
                self.dir_path = os.path.abspath(self.dir_name)
                break
    
    """
    Webページ上のPDFファイルのURLを取得し、絶対パスとファイル名を抽出して辞書に格納する関数
    """
    def get_pdfs(self):

        # WebページのHTML情報を取得
        res = requests.get(self.base_url)

        # requestsで取得した情報をBeautifulSoupに渡す
        soup = BeautifulSoup(res.content, "lxml")

        # PDFファイルのパスを含む<a>要素を全て取得
        soup_pdf = soup.find_all(href = re.compile('\.pdf'))


        # PDFファイルのファイル名とパスを取得し、辞書に格納

        # ==================== 内包表記を使った辞書の作成方法 ====================

        # PDFファイルのパスをリストに格納
        pdf_paths = [pdf.attrs['href'] for pdf in soup_pdf]
        # PDFファイルのパスから取得したファイル名をリストに格納
        file_names = [pdf_url.split('/')[-1] for pdf_url in pdf_paths]
        # PDFファイルのURLをリストに格納
        pdf_urls = [urljoin(self.base_url, pdf_url.replace(' ', '%20')) for pdf_url in pdf_paths]
        # PDFファイル名とURLを辞書に格納
        pdf_dict = {name:base_url for name, base_url in zip(file_names, pdf_urls)}


        # ==================== 内包表記を使わない方法 ====================

        # pdf_dict = {} # keys = file_name, values = pdf_urls
        # for pdf in soup_pdf:
        #     # PDFファイルのパスを取得
        #     pdf_path = pdf.attrs['href']
        #     # PDFファイル名を取得
        #     file_name = pdf_path.split('/')[-1]
        #     # PDFファイルのURLを取得
        #     pdf_url = urljoin(self.base_url, pdf_path.replace(' ', '%20'))

        #     pdf_dict[file_name] = pdf_url


        return pdf_dict

    """
    ファイルを保存する関数
    """
    def save_file(self, file_name, file_content, mode='wb'):
        with open(os.path.join(self.dir_path, file_name), mode) as f:
            f.write(file_content)


    """
    保存用ディレクトリに、Webページ上の全pdfファイル保存されているのかを確認する関数
    """
    def check_saved_pdfs(self, scraped_pdfs, saved_dir):
        num_scraped = len(scraped_pdfs)
        num_saved = len(os.listdir(saved_dir))
        
        if num_scraped == num_saved:
            return 'webページ上の全てのpdfファイルが保存されました。'
        else:
            print('一部のファイルが保存されませんでした。')
            return f'{num_saved}/{num_scraped}'

    """実行関数"""
    def main(self):

        """
        スクレイピングに用いるWebページからpdfファイル名と絶対パスを抽出し、辞書に格納
        """

        pdf_dict = self.get_pdfs()


        """pdfファイルを保存 """

        # 保存先のディレクトリの絶対path
        save_path = self.dir_path

        # save_pdfsインスタンスのsave_fileメソッドを変数に格納
        save_file = self.save_file

        # requests.getメソッドを変数resに格納
        res = requests.get

        # 処理時間の測定を開始
        # start = time.perf_counter()

        # webページ上の全てのpdfファイルを指定したディレクトリに保存
        for file_name, pdf_path in pdf_dict.items():
            res_p = res(pdf_path)
            if res_p.status_code == 200:
                file_content = res_p.content
                save_file(file_name, file_content)

            # 2秒スリープ
            time.sleep(2)
        
        # 処理時間の表示
        # print(time.perf_counter()-start)

        # pdfファイルの保存先を表示
        print(f'保存先 > {save_path}')
        # Webページ上のpdfファイルが、全て保存されたかを確認
        print(self.check_saved_pdfs(pdf_dict, save_path))


"""実行"""

if __name__ == '__main__':
    save_pdfs = SavePDFs()
    save_pdfs.main()
