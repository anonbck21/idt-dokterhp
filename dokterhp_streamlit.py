import streamlit as st

# Judul aplikasi
st.title("🔧 DokterHP v1 By IDT")
st.subheader("Asisten Diagnosa & Saran Perbaikan HP")

# Contoh data kerusakan
database = {
    "Tidak bisa di-charge": {
        "diagnosa": ["IC charging rusak", "Port USB kotor", "Baterai drop"],
        "saran": ["Coba kabel & adaptor lain", "Bersihkan port", "Cek baterai"]
    },
    "Layar bergaris / flicker": {
        "diagnosa": ["LCD rusak", "IC display bermasalah"],
        "saran": ["Ganti LCD", "Periksa jalur konektor LCD", "Cek IC display"]
    }
}

# Dropdown gejala
symptom = st.selectbox("📱 Pilih Gejala", list(database.keys()))

if st.button("🔍 Jalankan Diagnosa"):
    st.write("### 🩺 Diagnosa")
    for d in database[symptom]["diagnosa"]:
        st.write("- " + d)
    st.write("### 🛠️ Saran Perbaikan")
    for s in database[symptom]["saran"]:
        st.write("- " + s)
