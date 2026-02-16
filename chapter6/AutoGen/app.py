### app.py 实现
import streamlit as st
import requests
import time
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="比特币价格追踪器",
    page_icon="💰",
    layout="centered"
)

# 自定义CSS样式
st.markdown("""
<style>
.big-font {
    font-size:30px !important;
    font-weight: bold;
}
.price-container {
    background-color: #f0f2f6;
    padding: 20px;
    border-radius: 10px;
    margin: 10px 0;
}
.positive {
    color: #00cc00;
    font-weight: bold;
}
.negative {
    color: #ff4444;
    font-weight: bold;
}
.refresh-btn {
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 10px 20px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
    margin: 4px 2px;
    cursor: pointer;
    border-radius: 5px;
}
</style>
""", unsafe_allow_html=True)

def fetch_bitcoin_price():
    """从CoinGecko API获取比特币价格数据"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "bitcoin",
            "vs_currencies": "usd",
            "include_24hr_change": "true"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        bitcoin_data = data['bitcoin']
        
        return {
            'price': bitcoin_data['usd'],
            'change_24h': bitcoin_data['usd_24h_change']
        }
    except requests.exceptions.RequestException as e:
        st.error(f"网络请求错误: {str(e)}")
        return None
    except KeyError as e:
        st.error("API返回数据格式错误")
        return None
    except Exception as e:
        st.error(f"未知错误: {str(e)}")
        return None

def format_price(price):
    """格式化价格显示"""
    if price is None:
        return "N/A"
    return f"${price:,.2f}"

def format_change(change):
    """格式化24小时变化显示"""
    if change is None:
        return "N/A"
    
    if change >= 0:
        return f"+{change:.2f}%"
    else:
        return f"{change:.2f}%"

def get_change_class(change):
    """获取变化的CSS类名"""
    if change is None:
        return ""
    return "positive" if change >= 0 else "negative"

def main():
    st.title("💰 比特币价格追踪器")
    st.markdown("实时查看比特币( BTC )的最新价格和24小时变化趋势")
    
    # 初始化session state
    if 'last_update' not in st.session_state:
        st.session_state.last_update = None
        st.session_state.price_data = None
    
    # 创建刷新按钮
    col1, col2 = st.columns([1, 4])
    with col1:
        refresh_button = st.button("🔄 刷新价格")
    
    # 显示最后更新时间
    if st.session_state.last_update:
        with col2:
            st.caption(f"最后更新: {st.session_state.last_update}")
    
    # 获取数据
    if refresh_button or st.session_state.price_data is None:
        with st.spinner("正在获取最新比特币价格..."):
            price_data = fetch_bitcoin_price()
            if price_data:
                st.session_state.price_data = price_data
                st.session_state.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 显示数据
    if st.session_state.price_data:
        price = st.session_state.price_data['price']
        change_24h = st.session_state.price_data['change_24h']
        
        # 当前价格显示
        st.markdown('<div class="price-container">', unsafe_allow_html=True)
        st.markdown(f'<p class="big-font">当前价格</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-size: 24px; font-weight: bold;">{format_price(price)}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 24小时变化显示
        st.markdown('<div class="price-container">', unsafe_allow_html=True)
        st.markdown('<p class="big-font">24小时变化</p>', unsafe_allow_html=True)
        change_formatted = format_change(change_24h)
        change_class = get_change_class(change_24h)
        st.markdown(f'<p class="{change_class}" style="font-size: 20px;">{change_formatted}</p>', unsafe_allow_html=True)
        st.markdown(f'<p>涨跌额: ${price * (change_24h / 100):+.2f}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 自动刷新提示
        st.info("提示: 点击上方的刷新按钮获取最新价格")
    else:
        st.warning("暂无数据，请点击刷新按钮获取最新价格")

if __name__ == "__main__":
    main()