"""Categories – Quản lý danh mục."""

import streamlit as st
from services.category_service import CategoryService
from ui.components import page_header, empty_state


CATEGORY_TYPE_LABELS = {
    "income": "💰 Thu nhập",
    "expense_fixed": "📌 Chi phí cố định",
    "expense_variable": "🛒 Chi phí biến đổi",
    "saving": "🏦 Tiết kiệm",
    "transfer": "🔄 Chuyển khoản",
}


def render_categories():
    user_id = st.session_state["user_id"]
    page_header("Danh mục", "📂")

    cat_service = CategoryService()

    tab_list, tab_add_cat, tab_add_sub = st.tabs([
        "📋 Danh sách", "➕ Thêm nhóm", "➕ Thêm danh mục con",
    ])

    categories = cat_service.get_categories(user_id) or []

    # ── List ──
    with tab_list:
        if not categories:
            empty_state("Chưa có danh mục nào", "📂")
        else:
            for cat in categories:
                type_label = CATEGORY_TYPE_LABELS.get(cat.type, cat.type)
                subs = cat_service.get_subcategories(cat.id)
                sub_text = ", ".join(s.name for s in subs) if subs else "Chưa có danh mục con"
                with st.expander(f"{cat.icon or '📁'} {cat.name}  —  {type_label}"):
                    st.write(f"**Danh mục con:** {sub_text}")
                    if not cat.is_system:
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("🗑️ Xoá nhóm", key=f"del_cat_{cat.id}"):
                                ok, msg = cat_service.delete_category(cat.id)
                                st.success(msg) if ok else st.error(msg)
                                if ok:
                                    st.rerun()
                        with c2:
                            if subs:
                                sub_to_del = st.selectbox(
                                    "Xoá danh mục con",
                                    [s.id for s in subs],
                                    format_func=lambda x: next(
                                        (s.name for s in subs if s.id == x), ""
                                    ),
                                    key=f"sub_del_{cat.id}",
                                )
                                if st.button("🗑️ Xoá", key=f"del_sub_{cat.id}"):
                                    ok, msg = cat_service.delete_subcategory(sub_to_del)
                                    st.success(msg) if ok else st.error(msg)
                                    if ok:
                                        st.rerun()

    # ── Add category ──
    with tab_add_cat:
        with st.form("add_cat_form"):
            name = st.text_input("Tên nhóm *", placeholder="Ăn uống, Lương...")
            cat_type = st.selectbox(
                "Loại *",
                list(CATEGORY_TYPE_LABELS.keys()),
                format_func=lambda x: CATEGORY_TYPE_LABELS[x],
            )
            icon = st.text_input("Icon (emoji)", placeholder="🍔")
            color = st.color_picker("Màu", value="#6C5CE7")

            if st.form_submit_button("✅ Tạo nhóm", use_container_width=True):
                if not name.strip():
                    st.error("Vui lòng nhập tên")
                else:
                    ok, msg = cat_service.create_category(
                        user_id, name.strip(), cat_type, icon.strip(), color,
                    )
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    # ── Add subcategory ──
    with tab_add_sub:
        if not categories:
            st.warning("Vui lòng tạo nhóm danh mục trước")
        else:
            with st.form("add_sub_form"):
                cat_id = st.selectbox(
                    "Thuộc nhóm *",
                    [c.id for c in categories],
                    format_func=lambda x: next(
                        (c.name for c in categories if c.id == x), ""
                    ),
                )
                sub_name = st.text_input("Tên danh mục con *")

                if st.form_submit_button("✅ Tạo danh mục con", use_container_width=True):
                    if not sub_name.strip():
                        st.error("Vui lòng nhập tên")
                    else:
                        ok, msg = cat_service.create_subcategory(cat_id, sub_name.strip())
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
