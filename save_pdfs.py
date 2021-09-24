# -*- coding: utf-8 -*-
# 必要なライブラリ、モジュールをインポート

# import sys
import os
import re
import shutil
import time

import requests
from bs4 import BeautifulSoup


# Webページ上のpdfのURLを取得し、絶対パスとファイル名を抽出して辞書に格納する関数
def get_pdf_url(url):
    # WebページのHTML情報を取得
    res = requests.get(url)

    # 日本語が文字化けする可能性があるため、エンコードを"UTF-8"に指定
    res.encoding = 'UTF-8'

    # requestsで取得した情報をBeautifulSoupに渡す
    soup = BeautifulSoup(res.text)

    # すべてのpdfファイルの情報を抽出
    soup_pdf = soup.find_all(href = re.compile('\.pdf'))

    # WebページのURLから、ドメイン名末尾までの文字列を取得
    base_url = url.replace('//', '<<>>').split('/')[0].replace('<<>>', '//') + '/'

    # pdfファイルのファイル名とパスを取得し、辞書に格納
    pdf_dict = {} # keys = file_name, values = path
    for pdf in soup_pdf:
        pdf_url = pdf.attrs['href']
        # pdfのURLのうち、"/"で区切らた最後の部分をファイル名に使用
        file_name = pdf_url.split('/')[-1]
        pdf_path = pdf_url.replace('../', '').replace(' ', '%20')

        if base_url in pdf_url:
            download_url = pdf_url
        else:
            download_url = base_url + pdf_path
        
        pdf_dict[file_name] = download_url

    return pdf_dict


# ファイルを保存するための関数を作成
def save_file_at_dir(dir_name, file_name, file_content, mode='wb'):
    os.makedirs(dir_name, exist_ok=True) # 保存用のディレクトリを作成
    with open(os.path.join(dir_name, file_name), mode) as f:
        f.write(file_content)


# 全てのpdfファイルが、指定のディレクトリに保存されているか確認する関数
def check_saved_pdf_files(scraped_pdf, saved_dir):
    num_scraped_pdf = len(scraped_pdf)
    num_saved_pdf = len(os.listdir(saved_dir))
    
    if num_scraped_pdf == num_saved_pdf:
        return 'webページ上の全てのファイルが保存されました。'
    else:
        print('一部のファイルが保存されませんでした。')
        return f'{num_saved_pdf}/{num_scraped_pdf}'


# 実行
if __name__ == '__main__':

    """
    スクレイピングを行うWebページからpdfファイル名と絶対パスを抽出し、辞書に格納
    """
    url = input('スクレイピングしたいURLを入力してください。 > ')

    # # "EXIT"入力によるプログラム終了
    # if url == 'EXIT':
    #     sys.exit()

    pdf_dict = get_pdf_url(url)
    time.sleep(1)

    """
    保存先を指定
    """
    input_name = input('ファイルを保存する新しいディレクトリ(フォルダ)の名前、またはパスを指定してください。\n特に希望がなければ"Auto"を入力してください。 > ')
    
    # # "EXIT"入力によるプログラム終了
    # if input_path == 'EXIT':
    #     sys.exit()

    if input_name == 'Auto':
        dir_name = 'Saved_PDFs-1'
    else:
        dir_name = input_name
        
    # 重複するディレクトリ名の処理
    while os.path.isdir(dir_name):
        if dir_name.split('-')[0] == 'Saved_PDFs':
            saved_pdf_ver = int(dir_name.split('-')[1])
            update_ver = saved_pdf_ver + 1
            dir_name = './Saved_PDFs-{}'.format(update_ver)
            continue

        print('保存先に指定したディレクトリ(フォルダ)は既に存在しています。')
        print('新しいディレクトリ(フォルダ)名で保存先を指定してください。')
        print('-'*30)

        judge_delete_dir = input('保存先を指定する前に、既存のディレクトリ(フォルダ)を削除する場合は"Delete"を入力してください。\n削除しない場合は他のキーを押してください。 > ')
        if judge_delete_dir == 'Delete':
            shutil.rmtree(dir_name) # 保存先のディレクトリが存在していた場合、そのディレクトリを削除
            print('既存のディレクトリ(フォルダ)を削除しました。')
        reinput_path = input('保存先を指定してください。特に希望がなければ"Auto"を入力してください。 > ')
        dir_name = 'Saved_PDFs-1' if reinput_path == 'Auto' else reinput_path

    dir_path = os.path.abspath(dir_name)
    for file_name, pdf_path in pdf_dict.items():

        r = requests.get(pdf_path)

        if r.status_code == 200:
            file_content = r.content
            save_file_at_dir(dir_path, file_name, file_content, mode="wb")

        # 2秒スリープ
        time.sleep(2)
    

    print('保存先 > {}'.format(dir_path))
    print(check_saved_pdf_files(pdf_dict, dir_path))
