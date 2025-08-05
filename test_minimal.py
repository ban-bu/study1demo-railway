#!/usr/bin/env python3
"""
最小化Streamlit测试应用
用于验证Railway部署配置
"""

import streamlit as st
import os

# 页面配置
st.set_page_config(
    page_title="Railway Test",
    page_icon="🚀",
    layout="centered"
)

def main():
    st.title("🚀 Railway部署测试")
    st.success("如果你能看到这个页面，说明Streamlit在Railway上运行正常！")
    
    # 显示环境信息
    st.subheader("环境信息")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("端口", os.environ.get('PORT', '未设置'))
        st.metric("Python版本", f"{os.sys.version_info.major}.{os.sys.version_info.minor}")
    
    with col2:
        st.metric("Streamlit版本", st.__version__)
        st.metric("Railway环境", "是" if os.environ.get('RAILWAY_ENVIRONMENT') else "否")
    
    # 简单的交互功能
    st.subheader("功能测试")
    name = st.text_input("输入你的名字")
    if name:
        st.write(f"你好，{name}！Railway部署成功 🎉")
    
    if st.button("测试按钮"):
        st.balloons()
        st.success("按钮点击成功！")

if __name__ == "__main__":
    main()