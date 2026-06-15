import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import time
from src.config import SELECTED_FEATURES
from src.preprocessing import clean_network_data, select_features

MODEL_PATH = "outputs/models/random_forest.pkl"
SCALER_PATH = "outputs/models/scaler.pkl"


st.set_page_config(
    page_title="NIDS Demo",
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
    col3.metric("Các loại tấn công", "8 loại hình")
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
            "T1498 - Network Denial of Service: Các loại tấn công làm ngừng hoạt động dịch vụ mục tiêu bằng cách gửi luồng dữ liệu quá tải hoặc yêu cầu HTTP bất hợp pháp ",
            "T1498.001 - Network Flooding DoS: Tấn công từ chối dịch vụ phân tán, sử dụng nhiều thiết bị để gửi lưu lượng tấn công đồng thời làm ngừng hoạt động toàn bộ hệ thống mạng",
            "T1071 - Application Layer Protocol: Kẻ tấn công sử dụng giao thức ứng dụng chuẩn để điều khiển botnet",
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

    upload_file = st.file_uploader(
        "Tải lên tệp lưu lượng mạng (.csv)",
        type=["csv"]
    )

    if upload_file is None:
        st.info("Trạng thái: Đang chờ dữ liệu đầu vào...")
        if "prediction_results" in st.session_state:
            del st.session_state["prediction_results"]
        return

    try:
        df = pd.read_csv(upload_file)
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
                bat_dau = time.time()
                predictions = model.predict(X_model)
                ket_thuc = time.time()
                tong_thoi_gian = (ket_thuc - bat_dau) * 1000
                do_tre = tong_thoi_gian/len(X_model)
                st.session_state['current_latency'] = do_tre
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
    if total_flows > 0:
        attack_rate = attack_count / total_flows * 100
    else:
        attack_rate = 0
    st.session_state["bao_dong_gia"] = attack_rate

    if attack_count == 0:
        st.success("✅ MỨC ĐỘ NGUY HIỂM: THẤP | Hệ thống an toàn, không phát hiện xâm nhập")
    elif attack_count < 5:
        st.warning(f"⚠️ MỨC ĐỘ NGUY HIỂM: TRUNG BÌNH | Phát hiện {attack_count} luồng nghi vấn")
        
    else:
        st.error(f"🚨 MỨC ĐỘ NGUY HIỂM: CAO | Đã phát hiện {attack_count} luồng mạng độc hại!")
        

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
        if "Destination Port" in attack_df.columns:
            st.subheader("Các cổng đích bị tấn công nhiều nhất")
            top_ports = attack_df["Destination Port"].value_counts().head(10)
            st.bar_chart(top_ports)
        
        with col_chart:
            st.subheader("📊 Phân bố loại hình tấn công")
            attack_counts = attack_df["Predicted_Label"].value_counts()
            st.bar_chart(attack_counts, color="#ff4b4b") 

        with col_action:
            st.subheader("🛡️ Đề xuất ứng phó (Playbook)")
            st.warning(f"**Tấn công chủ đạo được phát hiện: {top_attack}**")
            st.info(f"MITRE ATT&CK: {anh_xa(top_attack)}")
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



    st.subheader("📄 Nhật ký sự kiện mạng (Network Event Logs)")
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
    json_data = result_df.to_json(orient = "records")
    st.download_button(
        label="📥 Xuất báo cáo sự cố(csv)",
        data=csv_data, 
        file_name="canh_bao_luu_luong.csv",
        mime="text/csv"
    )
    st.download_button(
        label= "📥 Xuất log (json)",
        data= json_data,
        file_name= "canh_bao_luu_luong.json",
        mime= "application/json"
        
    )
    st.info("""
        Lưu ý: Kết quả dự đoán được sinh ra bởi mô hình học máy và có thể tồn tại sai số. 
        Hệ thống hoạt động như một công cụ hỗ trợ giám sát, không thay thế hoàn toàn quá trình phân tích của chuyên gia an ninh mạng.
        """)
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
def anh_xa(label):
    if "PortScan" in label:
        return "T1046 - Network Service Scanning"
    elif "DDoS" in label:
        return "T1498.001 - Network Flooding DoS"
    elif "DoS" in label:
        return "T1498 - Network Denial of Service"
    elif "Bot" in label:
        return "T1071 - Application Layer Protocol"
    else:
        return "Chưa ánh xạ"


def show_threat_intel_page():
    st.title("Phân tích hiệu suất")
    
    st.markdown("""
     Trang web cung cấp cái nhìn chuyên sâu về năng lực thực tế của bộ não học máy (Random Forest), phân tích các rủi ro vận hành liên quan đến hiện tượng mất cân bằng dữ liệu, và giải thích cơ chế ra quyết định của mô hình.
    """)
    st.write("---")

    st.subheader("1. Chỉ số hiệu năng vận hành tổng thể")
    st.markdown("Đánh giá khả năng đáp ứng thời gian thực và kiểm soát báo động giả.")
    if "current_latency" in st.session_state:
        ht_do_tre = f"{st.session_state["current_latency"]: .3f} ms/luồng"
        trang_thai = "Đo lường thực tế"
    else:
        ht_do_tre = "None"
        trang_thai = "Không có thông tin"
    if "bao_dong_gia" in st.session_state:
        chi_so = f"{st.session_state["bao_dong_gia"]: .2f}%"
    else:
        chi_so = "None" 
    col1, col2, col3 = st.columns(3)
    col1.metric("Độ chính xác kiểm thử (Accuracy)", "99.31%", "Đạt chuẩn phân tích")
    col2.metric("Tỷ lệ báo động tấn công", chi_so, delta_color="inverse")
    col3.metric("Độ trễ suy luận", ht_do_tre, trang_thai) 

    st.write("---")

    st.subheader("2. Năng lực nhận diện theo từng loại hình tấn công")
    st.markdown("""
    Bảng dữ liệu dưới được lấy từ bảng thông số kỹ thuật đánh giá mô hình trên tập test
    """)

    metrics_data = {
        "Các loại hình tấn công": [
            "BENIGN (Lưu lượng sạch)", 
           "Bot",
           "DDoS",
           "DoS GoldenEye",
           "DoS Hulk",
           "DoS SLowhttptest",
           "DoS slowloris",
           "PortScan"
        ],
        "Độ tin cậy cảnh báo (Precision)": ["99.57%", "85.7%","99.57%", "97.78%", "97.07%", "95.92%", "100%", "99.28%" ],
        "Tỷ lệ phát hiện sự cố (Recall)": ["99.61%", "33.33%", "99.39%", "94.62%", "97.31%", "97.92%", "92.31%", "99.93%" ],
        "Chỉ số toàn vẹn (F1-Score)": ["99.55%", "48%", "99.48%", "96.17%", "97.19%", "96.91%", "96%", "99.6%" ],
        "Đánh giá rủi ro bỏ sót": ["🟢 An toàn", "🔴 Cảnh báo cao", "🟢 Rất thấp", "🟢 Rất thấp", "🟢 Rất thấp","🟢 Rất thấp", "🟢 Rất thấp", "🟢 Rất thấp"]
    }
    
    df_metrics = pd.DataFrame(metrics_data)
    st.dataframe(df_metrics, use_container_width=True)

    st.markdown("#### Phân tích các đặc tính dữ liệu thực tế:")
    
    tab_bot, tab_infil = st.tabs([" Nhãn Bot", "Nhãn Infiltration"])
    
    with tab_bot:
        st.warning("""
        **Nguyên nhân chỉ số nhãn Bot thấp (33.33% Recall):**
        * **Đặc tính kỹ thuật:** Trái ngược với các cuộc tấn công ồn ào như DoS hay PortScan, các bot độc hại khi giao tiếp với máy chủ C&C (Command & Control) thường cố tình ngụy trang luồng dữ liệu giống hệt hành vi truy cập HTTP/DNS hợp lệ của người dùng bình thường. Nhịp độ gửi gói tin rất chậm và kích thước gói tin nhỏ làm lu mờ ranh giới phân loại.
        * **Mất cân bằng dữ liệu:** Trong 100,000 dòng dữ liệu luồng mạng thực tế, tỷ lệ phân phối của nhãn Bot chiếm số lượng rất nhỏ. Thuật toán Random Forest khi tối ưu hóa hàm mục tiêu sẽ bị thiên vị về phía các lớp đa số như BENIGN hay DoS.
        
        **Khuyến nghị cho hệ thống:** Đối với loại tấn công Botnet, không nên chỉ dựa vào mô hình phân loại Flow-based. Các chuyên gia an ninh mạng cần kích hoạt thêm các công cụ phân tích sâu gói tin kết hợp giám sát danh tiếng IP.
        """)

    with tab_infil:
        st.info("""
        **Quyết định tiền xử lý: Loại bỏ hoàn toàn nhãn Infiltration trước khi huấn luyện.**
        * **Lý do kỹ thuật: Lớp Infiltration trong tập dữ liệu gốc có số lượng mẫu cực kỳ khan hiếm (chiếm 2/100000 mẫu). Việc giữ lại lớp này sẽ khiến mô hình gặp hiện tượng Overfitting nghiêm trọng, học máy không thể bóc tách được các luật phân phối tổng quát cho hành vi xâm nhập này mà chỉ sinh ra các cảnh báo nhiễu.
        * Thay vì ép mô hình học một lớp dữ liệu không đủ đại diện, nhóm quyết định cô lập lớp này để tập trung tài nguyên tính toán vào việc tối ưu hóa các lớp đe dọa phổ biến hơn.
        """)

    st.write("---")

    st.subheader("3. Trọng số đóng góp")
    st.markdown("""
    Biểu đồ dưới đây thể hiện trọng số đóng góp thực tế của 12 đặc trưng mạng cốt lõi mà mô hình Random Forest dựa vào để đưa ra dự đoán:
    """)

    col_chart, col_explain = st.columns([1.3, 1])
    
    with col_chart:
        importances = {
            "Average Packet Size": 0.194782,
            "Packet Length Std": 0.188247,
            "Packet Length Mean": 0.147269,
            "Total Fwd Packets": 0.088905,
            "Flow IAT Std": 0.078782,
            "Flow Duration": 0.067494,
            "Flow IAT Mean": 0.058912,
            "Total Backward Packets": 0.056371,
            "Flow Bytes/s": 0.049383,
            "Flow Packets/s": 0.034665,
            "ACK Flag Count": 0.033434,
            "SYN Flag Count": 0.001756
        }
        
        df_imp = pd.DataFrame({
            "Đặc trưng luồng mạng": list(importances.keys()),
            "Trọng số đóng góp": list(importances.values())
        }).sort_values(by="Trọng số đóng góp", ascending=True)
        
        st.bar_chart(df_imp.set_index("Đặc trưng luồng mạng"), color="#326FB1")

    with col_explain:
        st.markdown("##### Nhận xét trọng số ảnh hưởng của các đặc trưng:")
        st.markdown("""
        * Nhóm kích thước gói tin (Packet Size) chiếm hơn 50% mức độ quan trọng:
            Các đặc trưng như Average Packet Size, Packet Length Std và Packet Length Mean có mức độ ảnh hưởng cao trong mô hình. Điều này cho thấy kích thước và sự biến động của gói tin là dấu hiệu quan trọng để phân biệt lưu lượng bình thường với lưu lượng tấn công, đặc biệt trong các cuộc tấn công như DoS hoặc DDoS.
        * Nhóm Nhịp độ Thời gian (Timing & Flow IAT):
            Các đặc trưng như Flow IAT Std và Flow Duration giúp mô hình nhận biết nhịp độ bất thường của lưu lượng mạng. Với các hành vi như PortScan, công cụ quét thường gửi nhiều gói tin liên tiếp trong thời gian ngắn và có khoảng cách thời gian khá đều. Vì vậy, các đặc trưng về thời gian trở thành dấu hiệu quan trọng giúp mô hình phát hiện hoạt động quét cổng.
        """)

def main():
    model, scaler = load_model_and_scaler()

    st.sidebar.title("NIDS Demo")
    page = st.sidebar.radio(
        "Chọn trang",
        [
            "Giới thiệu",
            "Trung tâm dự đoán",
            "Phân tích hiệu suất"
        ]
    )

    if page == "Giới thiệu":
        show_intro_page()

    elif page == "Trung tâm dự đoán":
        show_predict_page(model, scaler)

    elif page == "Phân tích hiệu suất":
        show_threat_intel_page()
        
if __name__ == "__main__":
    main()