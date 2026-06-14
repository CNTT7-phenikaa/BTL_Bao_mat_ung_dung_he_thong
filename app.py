import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
from src.config import SELECTED_FEATURES
from src.preprocessing import clean_network_data, select_features

MODEL_PATH = "outputs/models/random_forest.pkl"
SCALER_PATH = "outputs/models/scaler.pkl"


st.set_page_config(
    page_title="NIDS Detection Demo",
    layout="wide"
)


@st.cache_resource
def load_model_and_scaler():
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    return model, scaler


def show_intro_page():
    st.title("🛡️ NIDS: Hệ thống phát hiện xâm nhập mạng ứng dụng Machine Learning")
    
    st.markdown("""
    **Network Intrusion Detection System (NIDS)** đóng vai trò là một cảm biến giám sát thụ động trong hạ tầng an ninh mạng. 
    Bằng cách ứng dụng thuật toán học máy **Random Forest**, hệ thống phân tích sâu các đặc trưng của luồng lưu lượng (Flow-based Analysis) để phát hiện sớm các hành vi bất thường, hỗ trợ đội ngũ SOC (Security Operations Center) phản ứng nhanh trước các cuộc tấn công hệ thống.
    """)

    st.write("---")
    st.subheader("Phạm vi giám sát và năng lực hệ thống")
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Mô hình sử dụng", "Random Forest")
    col2.metric("Đặc trưng trích xuất", "12 Features")
    col3.metric("Các loại tấn công", "7 loại hình")
    col4.metric("Độ chính xác kiểm thử", "99.31%")
    st.write("")

    st.subheader("Kiến trúc triển khai và luồng dữ liệu")
    
    col_text, col_img = st.columns([4, 6])
    
    with col_text:
        st.markdown("""
        Trong hạ tầng mạng doanh nghiệp hoặc môi trường điện toán đám mây, hệ thống NIDS không được đặt trực tiếp trên đường truyền chính. Thay vào đó, NIDS nhận bản sao lưu lượng mạng từ Switch thông qua cổng SPAN/Mirror Port để phân tích độc lập, nhờ đó không làm ảnh hưởng đến tốc độ truyền dữ liệu thực tế.

        **Cơ chế hoạt động:**

        1. **Traffic Mirroring:** Lưu lượng đi qua Switch được sao chép qua cổng SPAN/Mirror Port và gửi đến hệ thống NIDS. Luồng dữ liệu gốc vẫn tiếp tục đi đến Web Server hoặc Database Server như bình thường.

        2. **Feature Extraction:** Dữ liệu mạng được chuyển đổi thành các đặc trưng dạng flow-based như số lượng gói tin, kích thước gói tin và hành vi truyền nhận,....

        3. **ML Inference:** Sau khi được xử lý và chuẩn hóa, dữ liệu được đưa vào mô hình Random Forest để phân loại lưu lượng bình thường hoặc tấn công. Kết quả được hiển thị trên hệ thống demo và hỗ trợ đưa ra cảnh báo khi phát hiện bất thường.

        Nhờ cơ chế này, NIDS có thể giám sát và phát hiện dấu hiệu xâm nhập mà không làm gián đoạn lưu lượng mạng thật.
        """)

    with col_img:
        so_do_kt = "outputs/figures/so_do_kien_truc.png"
        st.image(so_do_kt, caption="Sơ đồ Kiến trúc Triển khai NIDS trong Hệ thống Mạng", use_container_width=True)

    st.write("---")

    st.subheader("Ánh xạ chiến thuật tấn công")
    st.markdown("""
    Để ngôn ngữ của hệ thống đồng bộ với các chuyên gia an ninh mạng quốc tế, các nhãn cảnh báo trong bộ dữ liệu CICIDS2017 được ánh xạ trực tiếp vào các kỹ thuật (Techniques) và chiến thuật (Tactics) của khung chuẩn **MITRE ATT&CK**:
    """)
    anh_xa = {
        "Loại tấn công": ["PortScan", "DoS Hulk / GoldenEye / Slowhttptest/ slowloris", "DDoS", "Bot", "BENIGN"],
        "Chiến thuật MITRE ATT&CK (Tactics)": [
            "Discovery (Phát hiện & thám sát môi trường mục tiêu)",
            "Impact (Gây ảnh hưởng hệ thống)",
            "Impact (Gây gián đoạn dịch vụ diện rộng)",
            "Command and Control (Điều khiển và lệnh)",
            "Normal Traffic"],
        "Mã Kỹ thuật (Technique ID)": [
            "T1046 - Network Service Scanning: Kẻ tấn công quét cổng mạng để xác định các dịch vụ đang chạy trên máy mục tiêu",
            "T1498 - Network Denial of Service:Các loại tấn công làm ngừng hoạt động dịch vụ mục tiêu bằng cách gửi luồng dữ liệu quá tải hoặc yêu cầu HTTP bất hợp pháp ",
            "T1498.001 - Network Flooding DoS: Tấn công từ chối dịch vụ phân tán, sử dụng nhiều thiết bị để gửi lưu lượng tấn công đồng thời làm ngừng hoạt động toàn bộ hệ thống mạng",
            "T1071 - Application Layer Protocol: : Kẻ tấn công sử dụng giao thức ứng dụng chuẩn để điều khiển botnet",
            "N/A"],
        "Mức độ Nguy cơ (Severity)": ["⚠️ Medium", "🚨 High", "🔴 Critical", "🔴 Critical", "🟢 Safe"]
    }
    st.table(pd.DataFrame(anh_xa))

    st.write("")

    with st.expander("Luồng xử lý của hệ thống"):
        st.markdown("""
        Hệ thống vận hành thông qua một chuỗi xử lý nghiêm ngặt từ lớp mạng lên lớp ứng dụng:
        
        ```
        Lưu lượng mạng thô
               ↓ (Trích xuất flow-based)
        Tệp dữ liệu CSV nguồn
               ↓ (Tiền xử lý dữ liệu)
        Lọc 12 đặc trưng tối ưu 
               ↓ (Chuẩn hóa thông qua Scaler)
        Dự đoán bằng mô hình ML (Random Forest Classifier)
               ↓ (Gửi tín hiệu cho trung tâm an ninh mạng)
        Bảng điều khiển & đề xuất hành động ứng phó
        ```
        """)
    st.subheader("Mục tiêu bảo mật của hệ thống")

    st.markdown("""
    Hệ thống được xây dựng nhằm hỗ trợ phát hiện sớm các hành vi bất thường trong lưu lượng mạng, 
    đặc biệt là các dấu hiệu liên quan đến quét cổng, tấn công từ chối dịch vụ và lưu lượng điều khiển botnet.

    Mục tiêu chính của hệ thống không phải thay thế hoàn toàn các giải pháp bảo mật thực tế, 
    mà là mô phỏng quy trình giám sát, phân tích và cảnh báo xâm nhập trong một hệ thống mạng.
    """)

def show_predict_page(model, scaler):
    st.title("🚨 Trung tâm cảnh báo sự cố an ninh mạng")

    st.markdown("""
    **Khu vực giám sát:** Tải lên tệp nhật ký lưu lượng mạng (.csv) được trích xuất từ thiết bị định tuyến hoặc tường lửa để phân tích.
    """)

    uploaded_file = st.file_uploader(
        "Tải lên tệp lưu lượng mạng (.csv)",
        type=["csv"]
    )

    if uploaded_file is None:
        st.info("Trạng thái: Đang chờ dữ liệu đầu vào...")
        if "prediction_results" in st.session_state:
            del st.session_state["prediction_results"]
        return

    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error("Lỗi đọc tệp. Vui lòng kiểm tra định dạng tệp.")
        return
    if st.button("Phân tích lưu lượng mạng", type="primary"):
        with st.spinner("Đang quét lưu lượng thông qua mô hình Random Forest..."):
            df_clean, X_model, missing_cols, removed_rows = prepare_uploaded_data(
                df,
                scaler,
            )

            if missing_cols:
                st.error("Tệp dữ liệu không hợp lệ. Thiếu các trường đặc trưng mạng sau:")
                st.write(missing_cols)
                return

            if df_clean is None or len(df_clean) == 0:
                st.error("Không có dữ liệu hợp lệ để phân tích.")
                return

            try:
                predictions = model.predict(X_model)
            except Exception as e:
                st.error("Lỗi suy luận mô hình.")
                return

            result_df = df_clean.copy()
            result_df["Predicted_Label"] = predictions
            
            st.session_state["prediction_results"] = result_df
            st.success("Hoàn tất quét lưu lượng!")
            
    if "prediction_results" in st.session_state:
        show_prediction_dashboard(st.session_state["prediction_results"])


def show_prediction_dashboard(result_df):
    st.markdown("---")
    st.subheader("🖥️ Bảng điều khiển trạng thái")

    total_flows = len(result_df)
    benign_count = (result_df["Predicted_Label"] == "BENIGN").sum()
    attack_count = total_flows - benign_count
    attack_rate = attack_count / total_flows * 100 if total_flows > 0 else 0

    if attack_count > 0:
        st.error(f"⚠️ MỨC ĐỘ NGUY HIỂM: CAO | Đã phát hiện {attack_count} luồng mạng độc hại!")
    else:
        st.success("✅ MỨC ĐỘ NGUY HIỂM: THẤP | Hệ thống an toàn, không phát hiện xâm nhập.")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tổng số connection", total_flows)
    col2.metric("Traffic hợp lệ (BENIGN)", benign_count)
    col3.metric("Traffic tấn công (ATTACK)", attack_count, delta_color="inverse")
    col4.metric("Tỷ lệ rủi ro", f"{attack_rate:.2f}%")
    st.markdown("---")

    if attack_count > 0:
        col_chart, col_action = st.columns([1, 1])
        
        attack_df = result_df[result_df["Predicted_Label"] != "BENIGN"]
        top_attack = attack_df["Predicted_Label"].value_counts().idxmax()
        
        with col_chart:
            st.subheader("📊 Phân bố Loại hình tấn công")
            attack_counts = attack_df["Predicted_Label"].value_counts()
            st.bar_chart(attack_counts, color="#ff4b4b") 

        with col_action:
            st.subheader("🛡️ Đề xuất ứng phó tự động (Playbook)")
            st.warning(f"**Tấn công chủ đạo được phát hiện: {top_attack}**")
            
            if "DoS" in top_attack or "DDoS" in top_attack:
                st.markdown("""
                **Hành động khuyến nghị:**
                * Kích hoạt Rule giới hạn tốc độ (Rate Limiting) trên WAF.
                * Tạm thời chặn các dải IP có số lượng gói tin truy vấn tăng đột biến.
                """)
                st.code("iptables -A INPUT -p tcp --dport 80 -m limit --limit 20/minute --limit-burst 100 -j ACCEPT", language="bash")
            elif "PortScan" in top_attack:
                st.markdown("""
                **Hành động khuyến nghị:**
                * Chặn ngay lập tức địa chỉ IP quét cổng.
                * Đóng các cổng không cần thiết ra Internet.
                """)
                st.code("iptables -A INPUT -p tcp --tcp-flags SYN,ACK,FIN,RST RST -m limit --limit 1/s -j ACCEPT", language="bash")
            else:
                st.markdown("**Hành động khuyến nghị:** Cách ly luồng mạng bị ảnh hưởng và gửi cảnh báo tới quản trị viên.")



    st.subheader("📄 Nhật ký Sự kiện Mạng (Network Event Logs)")
    unique_labels = sorted(result_df["Predicted_Label"].astype(str).unique().tolist())
    label_options = [
        "Tất cả lưu lượng (All Traffic)", 
        "Tất cả cảnh báo (All Attacks)"
    ] + unique_labels
    
    selected_label = st.selectbox("Lọc nhật ký", label_options)
    if selected_label == "Tất cả lưu lượng (All Traffic)":
        filtered_df = result_df 
    elif selected_label == "Tất cả cảnh báo (All Attacks)":
        filtered_df = result_df[result_df["Predicted_Label"] != "BENIGN"] 
    else:
        filtered_df = result_df[result_df["Predicted_Label"].astype(str) == selected_label]
    def highlight_attack(row):
        if row['Predicted_Label'] != 'BENIGN':
            return ['background-color: #ffe6e6; color: #a30000'] * len(row)
        else:
            return [''] * len(row)

    if not filtered_df.empty:
        display_columns = ["Destination Port", "Flow Duration", "Total Fwd Packets", "Predicted_Label"]
        display_columns = [col for col in display_columns if col in filtered_df.columns] 
    
        styled_df = filtered_df[display_columns].head(100).style.apply(highlight_attack, axis=1)
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.info("Không có nhật ký phù hợp với bộ lọc.")

    csv_data = result_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 Xuất báo cáo sự cố(csv)",
        data=csv_data,
        file_name="canh_bao_luu_luong.csv",
        mime="text/csv"
    )
def prepare_uploaded_data(df, scaler, already_scaled=False):

    missing_cols = [
        col for col in SELECTED_FEATURES
        if col not in df.columns
    ]

    if missing_cols:
        return None, None, missing_cols, 0

    original_rows = len(df)
    df_clean = clean_network_data(df, SELECTED_FEATURES)
    removed_rows = original_rows - len(df_clean)
    X = select_features(df_clean)
    if already_scaled:
        X_model = X
    else:
        X_model = scaler.transform(X)

    return df_clean, X_model, [], removed_rows


def show_evaluation_page():
    st.title("📊 Đánh giá mô hình")

    st.markdown("""
    Trang này dùng để hiển thị kết quả đánh giá mô hình đã huấn luyện.
    """)

    st.subheader("Mô hình được chọn")

    st.write("""
    Sau khi so sánh nhiều mô hình bằng Stratified K-Fold Cross Validation,
    mô hình Random Forest được chọn để sử dụng trong hệ thống demo.
    """)

    confusion_matrix_path = "outputs/figures/confusion_matrix.png"
    feature_importance_path = "outputs/figures/feature_importance.png"

    if os.path.exists(confusion_matrix_path):
        st.subheader("Confusion Matrix")
        st.image(confusion_matrix_path, use_container_width=True)
    else:
        st.warning("Chưa tìm thấy file confusion_matrix.png trong outputs/figures.")

    if os.path.exists(feature_importance_path):
        st.subheader("Feature Importance")
        st.image(feature_importance_path, use_container_width=True)
    else:
        st.warning("Chưa tìm thấy file feature_importance.png trong outputs/figures.")

def main():
    model, scaler = load_model_and_scaler()

    st.sidebar.title("NIDS Demo")
    page = st.sidebar.radio(
        "Chọn trang",
        [
            "Giới thiệu",
            "Trung tâm dự đoán",
            "Đánh giá mô hình"
        ]
    )

    if page == "Giới thiệu":
        show_intro_page()

    elif page == "Trung tâm dự đoán":
        show_predict_page(model, scaler)

    elif page == "Đánh giá mô hình":
        show_evaluation_page()



if __name__ == "__main__":
    main()