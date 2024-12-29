import requests
from bs4 import BeautifulSoup
import re
import jieba
from collections import Counter
import streamlit as st
from pyecharts import options as opts
from pyecharts.charts import WordCloud, Bar, Line, Pie, Scatter, Funnel, Radar
from streamlit.components.v1 import html
import pandas as pd

# 数据采集函数
def fetch_website_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        response.encoding = 'utf-8'  # 设置编码为 utf-8
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.title.string if soup.title else 'No title found'

    # 提取正文内容
    content_div = soup.find('div', class_='lemma-summary')
    if content_div:
        content = content_div.get_text(strip=True)
    else:
        content = soup.get_text(strip=True)

    return title, content

# 清理文本
def clean_text(text):
    text = re.sub(r'<[^>]*>', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    return text

# 词频统计函数
def get_word_frequency(content):
    word_frequency = Counter()
    cleaned_content = clean_text(content)

    # 分词
    words = [word for word in jieba.cut(cleaned_content) if word.strip()]
    word_frequency.update(words)

    return word_frequency

# 生成词云
def create_wordcloud(word_frequency):
    wordcloud_data = [(word, freq) for word, freq in word_frequency.items()]
    wordcloud = WordCloud() \
        .add("", wordcloud_data, word_size_range=[20, 100]) \
        .set_global_opts(title_opts=opts.TitleOpts(title="词云"))

    return wordcloud

# 生成柱状图
def create_bar_chart(word_frequency):
    words, frequencies = zip(*word_frequency.most_common(20))
    bar_chart = Bar() \
        .add_xaxis(list(words)) \
        .add_yaxis("Frequency", list(frequencies)) \
        .set_global_opts(title_opts=opts.TitleOpts(title="柱状图"))

    return bar_chart


# 生成折现图
def create_line_chart(word_frequency):
    words, frequencies = zip(*word_frequency.most_common(20))
    line_chart = Line() \
        .add_xaxis(list(words)) \
        .add_yaxis("Frequency", list(frequencies)) \
        .set_global_opts(title_opts=opts.TitleOpts(title="折线图"))

    return line_chart


def create_pie_chart(word_frequency):
    words, frequencies = zip(*word_frequency.most_common(20))
    pie_chart = Pie() \
        .add("", [list(z) for z in zip(words, frequencies)]) \
        .set_global_opts(title_opts=opts.TitleOpts(title="饼状图"))

    return pie_chart


# 创建散点图
def create_scatter_chart(word_frequency):
    words, frequencies = zip(*word_frequency.most_common(20))
    scatter_chart = Scatter() \
        .add_xaxis(list(words)) \
        .add_yaxis("Frequency", list(frequencies)) \
        .set_global_opts(title_opts=opts.TitleOpts(title="散点图"))

    return scatter_chart


# 创建漏斗图
def create_funnel_chart(word_frequency):
    words, frequencies = zip(*word_frequency.most_common(20))
    funnel_chart = Funnel() \
        .add("Words", [list(z) for z in zip(words, frequencies)]) \
        .set_global_opts(title_opts=opts.TitleOpts(title="漏斗图"))

    return funnel_chart


# 创建雷达图
def create_radar_chart(word_frequency):
    words, frequencies = zip(*word_frequency.most_common(20))
    radar_chart = Radar() \
        .add_schema(
        schema=[opts.RadarIndicatorItem(name=word, max_=max(frequencies)) for word in words]
    ) \
        .add("Frequency", [frequencies]) \
        .set_global_opts(title_opts=opts.TitleOpts(title="雷达图"))

    return radar_chart

# pyecharts渲染在Streamlit中
def st_pyecharts(chart):
    html(chart.render_embed(), height=500)

# Streamlit界面
def main():
    st.title("文章词频统计与词云生成")

    # 用户输入URL
    url = st.text_input("请输入文章URL")

    if 'content' not in st.session_state:
        st.session_state.content = None
        st.session_state.title = None
        st.session_state.word_frequency = None

    if st.button("抓取并统计词频"):
        title, content = fetch_website_content(url)

        if title and content:
            st.session_state.title = title
            st.session_state.content = content
            st.session_state.word_frequency = get_word_frequency(content)

    # 显示抓取的文章标题和内容
    if st.session_state.title and st.session_state.content:
        st.header(f"抓取的文章标题: {st.session_state.title}")
        st.write(st.session_state.content[:500] + '...')  # 显示文章的前500个字符

        word_frequency = st.session_state.word_frequency

        # 显示词频前20个
        most_common_words = word_frequency.most_common(20)
        st.subheader("词频排名前20的词汇")

        # # 创建 DataFrame 并显示
        df_most_common = pd.DataFrame(most_common_words, columns=["词汇", "频率"])
        # 显示 DataFrame，不进行样式高亮处理
        st.dataframe(df_most_common, height=500)

        # Sidebar筛选图形类型
        chart_type = st.sidebar.selectbox(
            "选择要展示的图形",
            ["词云", "柱状图", "折线图", "饼状图", "散点图", "漏斗图", "雷达图"]
        )

        # 根据选择的图形类型生成对应图形
        if chart_type == "词云":
            wordcloud = create_wordcloud(word_frequency)
            st_pyecharts(wordcloud)
        elif chart_type == "柱状图":
            bar_chart = create_bar_chart(word_frequency)
            st_pyecharts(bar_chart)
        elif chart_type == "折线图":
            line_chart = create_line_chart(word_frequency)
            st_pyecharts(line_chart)
        elif chart_type == "饼状图":
            pie_chart = create_pie_chart(word_frequency)
            st_pyecharts(pie_chart)
        elif chart_type == "散点图":
            scatter_chart = create_scatter_chart(word_frequency)
            st_pyecharts(scatter_chart)
        elif chart_type == "漏斗图":
            funnel_chart = create_funnel_chart(word_frequency)
            st_pyecharts(funnel_chart)
        elif chart_type == "雷达图":
            radar_chart = create_radar_chart(word_frequency)
            st_pyecharts(radar_chart)

        # Sidebar筛选低频词
        st.sidebar.subheader("筛选低频词")
        min_frequency = st.sidebar.slider("设置最小词频", 1, 20, 5)
        filtered_words = [(word, freq) for word, freq in word_frequency.items() if freq >= min_frequency]

        # 显示筛选后的词云
        st.subheader(f"筛选出词频大于{min_frequency}的词汇")
        filtered_wordcloud = create_wordcloud(Counter(dict(filtered_words)))
        st_pyecharts(filtered_wordcloud)

if __name__ == "__main__":
    main()