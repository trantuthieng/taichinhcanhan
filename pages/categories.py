import streamlit as st

from services.category_service import CategoryService
from ui.components import page_header


def render_categories() -> None:
    user_id = st.session_state["user_id"]
    page_header("Danh mục")

    categories = CategoryService.get_categories(user_id)

    st.subheader("Danh sách")
    if not categories:
        st.info("Chưa có danh mục")
    else:
        for cat in categories:
            with st.expander(f"{cat.name} ({cat.type})"):
                subs = CategoryService.get_subcategories(int(cat.id))
                if subs:
                    st.write("Danh mục con:")
                    st.write(", ".join([s.name for s in subs]))
                if int(cat.is_system) != 1 and st.button("Xóa danh mục", key=f"del_cat_{cat.id}"):
                    ok, msg = CategoryService.delete_category(int(cat.id))
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Thêm danh mục")
        with st.form("add_category"):
            name = st.text_input("Tên danh mục")
            cat_type = st.selectbox("Loại", ["income", "expense_fixed", "expense_variable", "saving", "transfer"])
            if st.form_submit_button("Tạo"):
                ok, msg = CategoryService.create_category(user_id, name.strip(), cat_type)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    with c2:
        st.subheader("Thêm danh mục con")
        with st.form("add_subcategory"):
            target_cat = st.selectbox("Danh mục cha", categories, format_func=lambda c: c.name) if categories else None
            sub_name = st.text_input("Tên danh mục con")
            if st.form_submit_button("Tạo"):
                if not target_cat:
                    st.error("Chưa có danh mục cha")
                else:
                    ok, msg = CategoryService.create_subcategory(int(target_cat.id), sub_name.strip())
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
