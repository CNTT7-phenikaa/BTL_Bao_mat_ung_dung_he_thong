import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
from src.config import SELECTED_FEATURES
from src.preprocessing import select_features

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
    st.title("🚨 Trung tâm Cảnh báo Sự cố (SOC Dashboard)")

    st.markdown("""
    **Khu vực Giám sát:** Tải lên tệp nhật ký lưu lượng mạng (CSV) được trích xuất từ thiết bị định tuyến hoặc tường lửa để phân tích.
    """)

    uploaded_file = st.file_uploader(
        "Tải lên tệp lưu lượng mạng (CSV)",
        type=["csv"]
    )

    if uploaded_file is None:
        st.info("Trạng thái: Đang chờ dữ liệu đầu vào...")
        return

    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error("Lỗi đọc tệp. Vui lòng kiểm tra định dạng CSV.")
        return

    # Chỉ hiển thị checkbox nếu người dùng thực sự cần (Có thể ẩn đi bằng expander cho giao diện gọn)
    with st.expander("⚙️ Cấu hình Nâng cao"):
        already_scaled = st.checkbox("Bỏ qua bước chuẩn hóa (Nếu tệp đã scale sẵn)", value=False)

    if st.button("Phân tích Lưu lượng Mạng", type="primary"):
        with st.spinner("Đang quét lưu lượng thông qua mô hình Random Forest..."):
            df_clean, X_model, missing_cols, removed_rows = prepare_uploaded_data(
                df,
                scaler,
                already_scaled=already_scaled
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
                st.error("Lỗi suy luận mô hình (Inference Error).")
                return

            result_df = df_clean.copy()
            result_df["Predicted_Label"] = predictions

        st.success("Hoàn tất quét lưu lượng!")
        show_prediction_dashboard(result_df)


def show_prediction_dashboard(result_df):
    st.markdown("---")
    st.subheader("🖥️ Bảng Điều khiển Trạng thái (System Status)")

    total_flows = len(result_df)
    benign_count = (result_df["Predicted_Label"] == "BENIGN").sum()
    attack_count = total_flows - benign_count
    attack_rate = attack_count / total_flows * 100 if total_flows > 0 else 0

    # 1. Trạng thái cảnh báo màu sắc theo Threat Level
    if attack_count > 0:
        st.error(f"⚠️ MỨC ĐỘ NGUY HIỂM: CAO | Đã phát hiện {attack_count} luồng mạng độc hại!")
    else:
        st.success("✅ MỨC ĐỘ NGUY HIỂM: THẤP | Hệ thống an toàn, không phát hiện xâm nhập.")

    # 2. Các chỉ số tổng quan (Metrics)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tổng số Connection", total_flows)
    col2.metric("Traffic Hợp lệ (BENIGN)", benign_count)
    col3.metric("Traffic Tấn công (ATTACK)", attack_count, delta_color="inverse")
    col4.metric("Tỷ lệ Rủi ro", f"{attack_rate:.2f}%")

    st.markdown("---")

    # 3. Phân tích loại hình tấn công
    if attack_count > 0:
        col_chart, col_action = st.columns([1, 1])
        
        attack_df = result_df[result_df["Predicted_Label"] != "BENIGN"]
        top_attack = attack_df["Predicted_Label"].value_counts().idxmax()
        
        with col_chart:
            st.subheader("📊 Phân bố Loại hình Tấn công")
            attack_counts = attack_df["Predicted_Label"].value_counts()
            st.bar_chart(attack_counts, color="#ff4b4b") # Đổi biểu đồ tấn công sang màu đỏ

        with col_action:
            st.subheader("🛡️ Đề xuất Ứng phó Tự động (Playbook)")
            st.warning(f"**Tấn công chủ đạo được phát hiện: {top_attack}**")
            
            # Giả lập logic đưa ra Playbook dựa trên loại tấn công
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
                * Đóng các cổng (Ports) không cần thiết ra Internet.
                """)
                st.code("iptables -A INPUT -p tcp --tcp-flags SYN,ACK,FIN,RST RST -m limit --limit 1/s -j ACCEPT", language="bash")
            else:
                st.markdown("**Hành động khuyến nghị:** Cách ly luồng mạng bị ảnh hưởng và gửi cảnh báo tới quản trị viên.")

    # 4. Nhật ký Sự kiện Hệ thống (Alert Logs)
    st.subheader("📄 Nhật ký Sự kiện Mạng (Network Event Logs)")
    
    label_options = ["Tất cả Cảnh báo (ATTACK)"] + sorted(result_df["Predicted_Label"].astype(str).unique().tolist())
    selected_label = st.selectbox("Lọc nhật ký", label_options)

    if selected_label == "Tất cả Cảnh báo (ATTACK)":
        filtered_df = result_df[result_df["Predicted_Label"] != "BENIGN"]
    else:
        filtered_df = result_df[result_df["Predicted_Label"].astype(str) == selected_label]

    # Style DataFrame: Bôi đỏ các dòng là Attack
    def highlight_attack(s):
        is_attack = s.Predicted_Label != 'BENIGN'
        return ['background-color: #ffe6e6; color: #a30000' if v else '' for v in is_attack]

    if not filtered_df.empty:
        # Chỉ hiển thị một số cột quan trọng cho đỡ rối mắt (bạn có thể thay đổi list này dựa vào dữ liệu thực tế)
        display_columns = ["Destination Port", "Flow Duration", "Total Fwd Packets", "Predicted_Label"]
        # Lọc các cột có tồn tại trong df
        display_columns = [col for col in display_columns if col in filtered_df.columns] 
        
        st.dataframe(filtered_df[display_columns].head(100).style.apply(highlight_attack, axis=1), use_container_width=True)
    else:
        st.info("Không có nhật ký phù hợp với bộ lọc.")

    csv_data = result_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 Xuất báo cáo sự cố (CSV)",
        data=csv_data,
        file_name="security_incident_report.csv",
        mime="text/csv"
    )


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

def prepare_uploaded_data(df, scaler, already_scaled=False):
    missing_cols = [
        col for col in SELECTED_FEATURES
        if col not in df.columns
    ]

    if missing_cols:
        return None, None, missing_cols, 0

    df_clean = df.copy()
    original_rows = len(df_clean)

    df_clean = df_clean.replace([np.inf, -np.inf], np.nan)
    df_clean = df_clean.dropna(subset=SELECTED_FEATURES)

    removed_rows = original_rows - len(df_clean)

    X = select_features(df_clean)

    if already_scaled:
        X_model = X
    else:
        X_model = scaler.transform(X)

    return df_clean, X_model, [], removed_rows


def main():
    model, scaler = load_model_and_scaler()

    st.sidebar.title("NIDS Demo")
    page = st.sidebar.radio(
        "Chọn trang",
        [
            "Giới thiệu",
            "Dự đoán từ file CSV",
            "Đánh giá mô hình"
        ]
    )

    if page == "Giới thiệu":
        show_intro_page()

    elif page == "Dự đoán từ file CSV":
        show_predict_page(model, scaler)

    elif page == "Đánh giá mô hình":
        show_evaluation_page()



if __name__ == "__main__":
    main()