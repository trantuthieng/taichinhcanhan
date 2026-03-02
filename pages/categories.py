"""Categories page - Quản lý danh mục."""

import streamlit as st
from services.category_service import CategoryService
from ui.components import section_header, empty_state


def render_categories():
    """Render trang quản lý danh mục."""
    user_id = st.session_state["user_id"]
    cat_service = CategoryService()

    st.markdown("## 📂 Danh mục")

    tab_list, tab_add_cat, tab_add_sub = st.tabs(["📋 Danh sách", "➕ Thêm nhóm", "➕ Thêm danh mục"])

    with tab_list:
        categories = cat_service.get_categories(user_id)
        if not categories:
            empty_state("Chưa có danh mục nào", "📂")
        else:
            for cat in categories:
                with st.expander(f"📁 {cat.name} ({cat.type})", expanded=False):
                    st.write(f"**Loại:** {'Thu nhập' if cat.type == 'income' else 'Chi tiêu' if cat.type == 'expense' else 'Khác'}")
                    if cat.icon:
                        st.write(f"**Icon:** {cat.icon}")

                    # Danh mục con
                    subcats = cat_service.get_subcategories(cat.id)
                    if subcats:
                        st.write("**Danh mục con:**")
                        for sub in subcats:
                            col1, col2 = st.columns([4, 1])
                            with col1:
                                st.write(f"  • {sub.name}")
                            with col2:
                                if not sub.is_system:
                                    if st.button("🗑️", key=f"del_sub_{sub.id}"):
                                        ok, msg = cat_service.delete_subcategory(user_id, sub.id)
                                        if ok:
                                            st.success(msg)
                                            st.rerun()
                                        else:
                                            st.error(msg)
                    else:
                        st.info("Chưa có danh mục con")

                    # Xóa nhóm
                    if not cat.is_system:
                        if st.button(f"🗑️ Xóa nhóm '{cat.name}'", key=f"del_cat_{cat.id}"):
                            ok, msg = cat_service.delete_category(user_id, cat.id)
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

    with tab_add_cat:
        with st.form("add_cat_form"):
            name = st.text_input("Tên nhóm danh mục *")
            cat_type = st.selectbox("Loại", ["expense", "income"],
                                     format_func=lambda x: "Chi tiêu" if x == "expense" else "Thu nhập")
            icon = st.text_input("Icon (emoji)", placeholder="🛒")

            if st.form_submit_button("✅ Tạo nhóm", use_container_width=True):
                if not name.strip():
                    st.error("Vui lòng nhập tên")
                else:
                    ok, msg = cat_service.create_category(user_id, name.strip(), cat_type, icon or None)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    with tab_add_sub:
        categories = cat_service.get_categories(user_id)
        if not categories:
            st.warning("Vui lòng tạo nhóm danh mục trước")
        else:
            with st.form("add_sub_form"):
                cat_id = st.selectbox(
                    "Thuộc nhóm *",
                    options=[c.id for c in categories],
                    format_func=lambda x: next((c.name for c in categories if c.id == x), ""),
                )
                sub_name = st.text_input("Tên danh mục con *")

                if st.form_submit_button("✅ Tạo danh mục con", use_container_width=True):
                    if not sub_name.strip():
                        st.error("Vui lòng nhập tên")
                    else:
                        ok, msg = cat_service.create_subcategory(user_id, cat_id, sub_name.strip())
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
