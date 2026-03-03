from datetime import date, datetime

import pandas as pd
import streamlit as st

from services.report_service import ReportService
from ui.components import page_header


def render_reports() -> None:
    user_id = st.session_state["user_id"]
    page_header("Báo cáo")

    trend = ReportService.get_monthly_trend(user_id, 12)
    if not trend:
        st.info("Chưa có dữ liệu báo cáo")
        return

    df = pd.DataFrame(trend)
    st.dataframe(df, use_container_width=True, hide_index=True)

    if {"month", "income", "expense"}.issubset(df.columns):
        chart_df = df[["month", "income", "expense"]].set_index("month")
        st.line_chart(chart_df)
