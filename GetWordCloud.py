# coding=utf8

from os import path
from wordcloud import WordCloud, ImageColorGenerator
import codecs
import matplotlib.pyplot as plt
from scipy.misc import imread
import jieba
from collections import Counter
import time
import re
import pynlpir
import logging
import argparse

logging.basicConfig(format="%(asctime)s: %(levelname)s: %(message)s", level=logging.INFO)

d = path.dirname(__file__)
font = path.join(d, "font/yegenyou.ttf")
stopwords = [line.strip() for line in codecs.open('txt/stopwords.txt', encoding='utf-8').readlines()]


def get_text(filepath, seg_type='nlpir'):
    '''
    获取生成词云文本的内容，分词去停用词后，返回词频字典
    :param filepath: xxx.txt
    :param seg_type: 分词的方式 ['nlpir', 'jieba']
    :return: {'a':5, 'b':2, ...}
    '''
    # Read the whole text.
    # filepath = filepath.decode('utf8')
    text = codecs.open(filepath, encoding='utf8').read()
    ch_text = only_ch(text)
    print 'just remain chinese text'
    # 处理文本
    all_words = nlpir_seg_txt(ch_text)
    if seg_type == 'nlpir':
        all_words = nlpir_seg_txt(ch_text)
    elif seg_type == 'jieba':
        all_words = jieba_seg_txt(ch_text)
    else:
        logging.error("bad segmentation type...")
    print 'has segged text...'
    # 计算词频
    # start = time.time()
    word_freq = Counter(all_words)
    print 'has gotten word_freq'
    # print word_freq
    # print 'generate word frequence dict elapse %f seconds' % (time.time() - start)
    return word_freq


def only_ch(text):
    # 只保留中文
    ch_pat = re.compile(ur'[\u4E00-\u9FA5]+')
    all_ch_text = ch_pat.findall(text)
    new_text = ''.join(all_ch_text)
    return new_text


def jieba_seg_txt(text):
    # jieba 分词并去停用词
    # 分词且去停用词
    segments = jieba.cut(text)
    # 去停用词
    remove_segments = [word for word in segments if word not in stopwords and len(word) > 1]
    return remove_segments


def nlpir_seg_txt(text):
    # nlpir 分词并用去停用词
    pynlpir.open()
    # 分词且去停用词
    segments = pynlpir.segment(text, pos_tagging=False, pos_english=False)
    # 去停用词
    remove_segments = [word for word in segments if word not in stopwords and len(word) > 1]
    pynlpir.close()
    return remove_segments


def plot_wordcloud(word_freqs, orig_pic, final_pic, type = 1):
    '''
    根据词频字典绘制词云
    :param word_freqs: {'a':5, 'b':2, ...}
    :param type: type=1 表示只用图片的轮廓, type=2 表示也使用图片的颜色
    :param orig_pic: 背景图片的路径
    :param final_pic: 生成图片保存的路径
    '''
    # read the mask / color image
    colorpic = imread(orig_pic)

    # Generate a word cloud image
    wordcloud = WordCloud(font_path=font,
                          background_color='white',
                          mask=colorpic,
                          random_state=42)
    wordcloud.generate_from_frequencies(word_freqs)
    # 从背景图片生成颜色值
    image_colors = ImageColorGenerator(colorpic)

    # 显示图片
    if type == 1:
        plt.imshow(wordcloud)
        plt.axis("off")
        # 绘制词云
        # plt.figure()
    if type == 2:
        # recolor wordcloud and show
        # we could also give color_func=image_colors directly in the constructor
        plt.imshow(wordcloud.recolor(color_func=image_colors))
        plt.axis("off")
    plt.show()
    wordcloud.to_file(final_pic)


def wordcloud_with_shape():
    parser = argparse.ArgumentParser(description='make wordcloud with special shape')
    parser.add_argument('text_dir', help="the txt file you need to generate wordcloud")
    parser.add_argument('img_dir', help="the image file you use as wordcloud's shape")
    parser.add_argument('res_dir', help="the wordcould picture's saving directory")
    parser.add_argument('-p', '--plot_type', default=1, choices=[1, 2],
                        help="1 - just use image ; 2 - use image shape&color")
    parser.add_argument('-s', '--seg_type', default='nlpir', choices=['nlpir', 'jieba'],
                        help="the way you segment your text")
    args = parser.parse_args()

    # get word frequency dictionary
    text_dir = args.text_dir.decode('gbk')
    img_dir = args.img_dir.decode('gbk')
    res_dir = args.img_dir.decode('gbk')
    word_freq_dict = get_text(text_dir, seg_type=args.seg_type)
    # plot wordcloud
    plot_wordcloud(word_freq_dict, img_dir, res_dir, type=args.plot_type)


if __name__ == '__main__':
    wordcloud_with_shape()