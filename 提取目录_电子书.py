import os
import re
import fitz  # 处理pdf
from ebooklib import epub  # 处理epub
import zipfile
from bs4 import BeautifulSoup
import pyperclip
import warnings

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

def extract_toc_from_pdf(file):  # https://pdfobject.com/examples/pdf-open-params.html
    toc_text = f'{file}\n'
    with fitz.open(file) as book:
        toc = book.get_toc()
        for level, title, page in toc:
            # if level >= 3:
            #     continue
            title = standardize_title(title)
            link = f"https://elib.wanyunhui.top/{file.replace(' ', '%20')}#page={page}"
            toc_text += f"{'  ' * (level - 1)}- [ ] [{title}](<{link}>)\n"
        print(f'已从 PDF 中提取目录: {file}')
    return toc_text

def extract_toc_from_epb(file):  # https://github.com/johnfactotum/foliate-js
    # 提取EPUB3目录(nav.xhtml)
    def parse_xht_toc(toc, file, path, level=1):
        toc_line = ''
        nav_points = toc.find_all('li', recursive=False)
        for nav_point in nav_points:
            title = standardize_title(nav_point.find('a').get_text(strip=True))
            link = f"https://elib.wanyunhui.top/foliate/reader.html?book={file.replace(' ', '%20')}&part={path}{nav_point.find('a')['href']}"
            toc_line += f"{'  ' * (level - 1)}- [ ] [{title}](<{link}>)\n"
            child_nav = nav_point.find('ol', recursive=False)
            if child_nav:  # 递归处理子项
                toc_line += parse_xht_toc(child_nav, file, path, level + 1)
        return toc_line
    # 提取EPUB2目录(toc.ncx)
    def parse_ncx_toc(toc, file, path, level=1):
        toc_line = ''
        nav_points = toc.find_all('navpoint', recursive=False)
        for nav_point in nav_points:
            title = standardize_title(nav_point.find('text').get_text(strip=True))
            link = f"https://elib.wanyunhui.top/foliate/reader.html?book={file.replace(' ', '%20')}&part={path}{nav_point.find('content')['src']}"
            toc_line += f"{'  ' * (level - 1)}- [ ] [{title}](<{link}>)\n"
            child_nav = nav_point.find('navpoint', recursive=False)
            if child_nav:  # 递归处理子项
                toc_line += parse_ncx_toc(nav_point, file, path, level + 1)
        return toc_line
    # 获取EPUB目录文件相对路径
    # def get_toc_path(epb_file, toc_file):
    #     with zipfile.ZipFile(epb_file, 'r') as zip_ref:
    #         temp_dir = os.path.basename(epb_file)[:-5]
    #         zip_ref.extractall(temp_dir)
    #         for root, _, files in os.walk(temp_dir):
    #             if toc_file in files:
    #                 rel_path = os.path.relpath(root, temp_dir)
    #                 return rel_path + '/' if rel_path != '.' else ''
    def get_toc_path(epb_file, toc_file):
        with zipfile.ZipFile(epb_file, 'r') as z:
            for name in z.namelist():
                if name.endswith(toc_file):
                    return os.path.dirname(name) + '/'
        return ''

    toc_text = f'{file}\n'
    book = epub.read_epub(file)
    for item in book.get_items():
        if isinstance(item, epub.EpubNav):
            path = get_toc_path(file, 'nav.xhtml')
            toc = BeautifulSoup(item.get_body_content(), 'lxml').find('ol')
            toc_text += parse_xht_toc(toc, file, path)
            print(f'已从EPUB3中提取目录: {file}')
            break
        elif isinstance(item, epub.EpubNcx):
            path = get_toc_path(file, 'toc.ncx')
            toc = BeautifulSoup(item.get_content(), 'lxml').find('navmap')
            toc_text += parse_ncx_toc(toc, file, path)
            print(f'已从EPUB2中提取目录: {file}')
            break
    return toc_text

def standardize_title(title):
    # 将中文数字转换为英文数字1-99(异常0)
    def chnnum_to_number(chnnum):      
        if len(chnnum) == 1:
            return chinese_numerals.get(chnnum, 10)
        elif chnnum[0] == '十':
            return 10 + chinese_numerals.get(chnnum[1])
        elif chnnum[1] == '十':
            return 10 * chinese_numerals.get(chnnum[0]) + chinese_numerals.get(chnnum[-1], 0)
        return 0
    # 将英文数字转换为英文字母A-I(异常Z)
    def number_to_letter(number):
        if 1 <= number <= 26:
            return chr(64 + number)
        return 'Z'

    chinese_numerals = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}
    # 统一章节标题为2位数字: 01 XXX (第一章: XXX | Chapter 1 XXX)
    if chp_match := re.match(r'(Chapter|第)\s*([0-9]+|[一二三四五六七八九十]+)\s*章?[、：:.]?\s*(.*)', title, re.IGNORECASE):
        chp_number = chp_match.group(2)
        if chp_number.isdigit():
            chp_number = int(chp_number)
        else:
            chp_number = chnnum_to_number(chp_number)
        return f'{chp_number:02d} {chp_match.group(3)}'
    # 统一附录标题为2位字母: AA XXX (附录一  XXX | Appendix. XXX)
    elif app_match := re.match(r'(Appendix|附录)\s*([A-Za-z1-9]|[一二三四五六七八九])?[、：:.]?\s*(.*)', title, re.IGNORECASE):
        app_letter = app_match.group(2)
        if app_letter is None:
            app_letter = 'A'
        elif app_letter.isalpha():
            app_letter = app_letter.upper()
        elif app_letter.isdigit():
            app_letter = number_to_letter(int(app_letter))
        else:
            app_letter = number_to_letter(chinese_numerals[app_letter])
        return f'A{app_letter} {app_match.group(3)}'
    return title

if __name__ == '__main__':
    all_texts = ''
    for file in os.listdir():
        if file.endswith('.pdf'):
            all_texts += f'{extract_toc_from_pdf(file)}\n'
        elif file.endswith('.epub'):
            all_texts += f'{extract_toc_from_epb(file)}\n'
    pyperclip.copy(all_texts)
