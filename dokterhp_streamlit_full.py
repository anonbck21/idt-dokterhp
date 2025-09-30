# dokterhp_streamlit_full.py
# ============================================================
# IDT-DokterHP V 1.01 (Streamlit - Full DB)
# - Platform: iPhone & Android
# - Dropdown: platform -> kategori -> gejala
# - Tampilkan diagnosa (detail) + saran perbaikan (langkah)
# - Export hasil ke TXT / PDF (download)
# - Footer copyright & contact
# ============================================================

import streamlit as st
from datetime import datetime
import textwrap
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

st.set_page_config(page_title="DokterHP v1 By IDT", page_icon="📱", layout="wide")

st.markdown("<h1 style='text-align: center; color: #0b6efd;'>🔧 DokterHP v1 By IDT</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #555;'>Asisten Diagnosa & Saran Perbaikan HP — iPhone & Android</p>", unsafe_allow_html=True)
st.write("---")

# ============================
# FULL DATABASE (iPhone + Android)
# ============================
DB = {
    "iPhone": {
        # Daya & Charging
        "Daya & Charging": {
            "Tidak bisa di-charge": {
                "diagnosa": [
                    "IC charging (mis. Tristar/Tigris/PMIC) rusak atau tidak berfungsi.",
                    "Port Lightning kotor/korosi atau pin tertekuk/putus.",
                    "Baterai mengalami kerusakan fisik atau NTC tidak terbaca.",
                    "Jalur proteksi atau fusible open, atau IC authentication aksesori menolak kabel."
                ],
                "saran": [
                    "1) Coba kabel & adaptor Apple original / MFi. Jika berhasil, kemungkinan kabel/charger.",
                    "2) Bersihkan port Lightning pakai udara tekan atau IPA, periksa korosi/pin.",
                    "3) Ukur tegangan VBUS saat charger terpasang (~5V atau sesuai fast charge).",
                    "4) Ukur arus charging pada power-supply bench; catat arus idle vs saat charge.",
                    "5) Jika tidak ada tegangan → periksa fusible / ferrite / jalur VBUS pada board.",
                    "6) Jika ada tegangan namun tidak mengisi → cek jalur ke PMIC dan IC charging; lakukan pengukuran regulator.",
                    "7) Ganti baterai original jika health rendah atau NTC bermasalah.",
                    "8) Jika terindikasi hardware, lakukan rework (reflow/reball) atau ganti IC charging/PMIC."
                ]
            },
            "Cepat habis baterai": {
                "diagnosa": [
                    "Baterai menurun kapasitas (cycle count tinggi).",
                    "Ada proses/system service yang boros daya (software).",
                    "Komponen short / boros arus pada board (mis. IC sensor/PMIC)."
                ],
                "saran": [
                    "1) Cek Battery Health lewat Settings; catat kapasitas maksimal (mAh atau %).",
                    "2) Lakukan test dengan baterai known-good.",
                    "3) Periksa aplikasi/layanan dengan konsumsi tinggi, lakukan reset/restore jika perlu.",
                    "4) Ukur arus standby; arus berlebih mengindikasikan short/consumption abnormal.",
                    "5) Periksa area PMIC untuk komponen panas; ukur continuity ground/supply."
                ]
            },
            "Overheating saat charge": {
                "diagnosa": [
                    "Baterai mengalami internal heating (cell fault).",
                    "IC charging/PMIC panas karena short atau kerusakan.",
                    "Penggunaan adaptor yang tidak sesuai (over-voltage)."
                ],
                "saran": [
                    "1) Stop charging segera, lepaskan baterai jika aman.",
                    "2) Gunakan thermal camera untuk mengidentifikasi hotspot.",
                    "3) Coba dengan baterai baru; jika masih panas, cek IC charging/PMIC.",
                    "4) Periksa jalur VBUS/ground untuk short; injeksi arus jika perlu.",
                    "5) Ganti baterai atau reball/replace IC yang rusak."
                ]
            },
            "Deteksi 'aksesori tidak didukung'": {
                "diagnosa": [
                    "Kabel/charger bukan original / MFi, resistor ID berbeda.",
                    "Port Lightning ada korosi / pin data bermasalah.",
                    "IC yang menangani autentikasi aksesori bermasalah."
                ],
                "saran": [
                    "1) Coba kabel & charger original Apple / MFi certified.",
                    "2) Bersihkan port, periksa resistor ID pada kabel (jika bisa).",
                    "3) Periksa jalur data D+/D- dan resistor pull-up/pull-down.",
                    "4) Jika aksesori original tetap dicekal, periksa IC authentication/PMIC."
                ]
            }
        },

        # Layar & Display
        "Layar & Display": {
            "Layar blank tapi ada suara": {
                "diagnosa": [
                    "Backlight IC/driver bermasalah.",
                    "FPC display terputus atau konektor longgar.",
                    "Panel LCD rusak."
                ],
                "saran": [
                    "1) Swap test dengan LCD known-good untuk verifikasi.",
                    "2) Ukur tegangan backlight (anode/cathode) saat boot.",
                    "3) Periksa continuity flex & konektor; ressolder atau ganti flex jika perlu.",
                    "4) Jika panel pengganti berhasil → ganti LCD; jika tidak → cek IC display."
                ]
            },
            "Layar bergaris / flicker": {
                "diagnosa": [
                    "Kerusakan panel LCD atau masalah solder joint pada IC display.",
                    "FPC kendor atau flex rusak."
                ],
                "saran": [
                    "1) Swap LCD, jika masih bergaris kemungkinan IC display.",
                    "2) Reflow / reball IC display bila perlu.",
                    "3) Periksa konektor FPC dan ganti flex jika perlu."
                ]
            },
            "Ghost touch": {
                "diagnosa": [
                    "Panel aftermarket / berkualitas rendah menyebabkan noise touch.",
                    "IC touch digitizer bermasalah atau ada interferensi tegangan."
                ],
                "saran": [
                    "1) Ganti dengan panel original & uji.",
                    "2) Perbaiki grounding dan periksa jalur touch untuk noise.",
                    "3) Reball/replace IC touch bila terkonfirmasi hardware."
                ]
            },
            "TrueTone tidak berfungsi": {
                "diagnosa": [
                    "Data kalibrasi (EEPROM) pada layar lama tidak dipindahkan.",
                    "Kalibrasi warna hilang saat pergantian panel."
                ],
                "saran": [
                    "1) Pindahkan EEPROM dari layar lama ke layar baru (jika model memungkinkan).",
                    "2) Gunakan tool programmer untuk restore data TrueTone jika tersedia.",
                    "3) Jika tidak memungkinkan -> informasikan customer bahwa fungsi tidak tersedia."
                ]
            }
        },

        # Audio
        "Audio": {
            "Mic tidak berfungsi": {
                "diagnosa": [
                    "Mic fisik rusak atau flexible mic putus.",
                    "Jalur mic (solder/jalur) putus atau short.",
                    "IC audio bermasalah."
                ],
                "saran": [
                    "1) Tes mic dengan voice memo / panggilan test.",
                    "2) Ganti modul mic atau dock flex mic.",
                    "3) Periksa continuity jalur mic ke IC audio.",
                    "4) Jika perlu, reball/replace IC audio."
                ]
            },
            "Speaker kecil / pecah": {
                "diagnosa": [
                    "Speaker kotor / terhalang atau membran rusak.",
                    "Masalah pada IC amplifier / jalur audio."
                ],
                "saran": [
                    "1) Bersihkan lubang speaker, lakukan swap test speaker.",
                    "2) Ganti speaker jika fisik rusak.",
                    "3) Periksa IC audio dan jalur menuju speaker."
                ]
            },
            "Ear speaker mati / kecil": {
                "diagnosa": [
                    "Ear speaker atau flex konektor rusak.",
                    "IC audio bermasalah."
                ],
                "saran": [
                    "1) Swap ear speaker.",
                    "2) Bersihkan & cek konektor flex ear speaker.",
                    "3) Jika berlanjut, periksa IC audio."
                ]
            },
            "Tidak ada suara saat panggilan": {
                "diagnosa": [
                    "Routing audio ke ear speaker gagal (flex/konektor).",
                    "IC audio problem."
                ],
                "saran": [
                    "1) Tes routing audio (voice memo / diagnostic).",
                    "2) Swap ear speaker, bersihkan konektor.",
                    "3) Jika tetap, reball/replace IC audio."
                ]
            }
        },

        # Kamera & FaceID
        "Kamera & FaceID": {
            "Kamera belakang tidak terdeteksi": {
                "diagnosa": [
                    "Flex kamera putus / tidak terpasang.",
                    "Modul kamera rusak.",
                    "IC camera interface bermasalah."
                ],
                "saran": [
                    "1) Swap modul kamera dengan known-good.",
                    "2) Periksa konektor kamera & continuity.",
                    "3) Jika tetap tidak terdeteksi, periksa IC camera atau jalur I2C/PMIC."
                ]
            },
            "Kamera depan buram": {
                "diagnosa": [
                    "Lensa kotor / goresan.",
                    "Kerusakan optik pada modul kamera."
                ],
                "saran": [
                    "1) Bersihkan lensa dengan IPA & kain microfiber.",
                    "2) Ganti modul kamera depan jika masih buram."
                ]
            },
            "Flash tidak berfungsi": {
                "diagnosa": [
                    "LED flash rusak atau jalur VCC flash terputus.",
                    "Driver flash / IC bermasalah."
                ],
                "saran": [
                    "1) Ukur tegangan saat trigger flash.",
                    "2) Jika tidak ada tegangan, periksa jalur VCC dan driver IC.",
                    "3) Ganti LED/driver jika perlu."
                ]
            },
            "Face ID error": {
                "diagnosa": [
                    "Flex flood illuminator atau dot projector rusak.",
                    "Kalibrasi / pairing Face ID hilang setelah servis."
                ],
                "saran": [
                    "1) Periksa konektor TrueDepth & flex, pastikan tidak ada kerusakan fisik.",
                    "2) Jika modul rusak, harus diganti sesuai prosedur (beberapa bagian tidak dapat dipisah karena security pairing).",
                    "3) Jika pairing hilang → kemungkinan perlu penggantian board/module asli."
                ]
            }
        },

        # Sinyal & Koneksi
        "Sinyal & Koneksi": {
            "Tidak ada layanan / searching terus": {
                "diagnosa": [
                    "Baseband / modem bermasalah atau PA/RF rusak.",
                    "Antenna disconnect / damage.",
                    "IMEI / NVRAM corrupt."
                ],
                "saran": [
                    "1) Periksa IMEI via *#06#; bila kosong → cek NVRAM / baseband.",
                    "2) Periksa jalur antena & solder joint PA/RF.",
                    "3) Jika terindikasi hardware → reball/replace baseband IC / RF."
                ]
            },
            "IMEI hilang": {
                "diagnosa": [
                    "Partition EFS/NVRAM corruption (umum di Android; pada iPhone kemungkinan due to baseband firmware).",
                    "Baseband firmware corrupt / hardware failure."
                ],
                "saran": [
                    "1) Periksa log panic/diagnostic untuk indikasi update/flash.",
                    "2) Gunakan tool service untuk restore NVRAM/IMEI jika ada backup.",
                    "3) Jika hardware, reball/replace baseband or logic board."
                ]
            },
            "WiFi abu-abu / tidak bisa diaktifkan": {
                "diagnosa": [
                    "IC WiFi/BT combo bermasalah atau firmware corrupt.",
                    "Antenna WiFi terputus."
                ],
                "saran": [
                    "1) Reset network / restore firmware.",
                    "2) Jika tetap, reball/replace IC WiFi atau periksa jalur antena."
                ]
            },
            "Bluetooth tidak jalan": {
                "diagnosa": [
                    "IC combo WiFi/BT rusak atau firmware corrupt."
                ],
                "saran": [
                    "1) Reset Bluetooth, hapus pair list, coba re-pair.",
                    "2) Reflash firmware atau replace IC WiFi/BT."
                ]
            }
        },

        # Sensor & Lainnya
        "Sensor & Lainnya": {
            "Proximity sensor tidak jalan": {
                "diagnosa": [
                    "Sensor proximity / flex rusak.",
                    "Konektor sensor longgar atau kalibrasi hilang."
                ],
                "saran": [
                    "1) Test proximity melalui diagnostic menu.",
                    "2) Ganti flex sensor atau perbaiki konektor.",
                    "3) Jika software related, coba restore."
                ]
            },
            "Touch ID tidak terbaca": {
                "diagnosa": [
                    "Home button flex / sensor Touch ID rusak.",
                    "Pairing Touch ID hilang."
                ],
                "saran": [
                    "1) Ganti home button original & lakukan pairing jika memungkinkan.",
                    "2) Jika pairing hilang → kemungkinan perlu ganti board/module."
                ]
            }
        },

        # Software & Boot
        "Software & Boot": {
            "Stuck logo Apple": {
                "diagnosa": [
                    "iOS corrupt / boot partition corrupt.",
                    "NAND / eMMC issue atau IC boot bermasalah."
                ],
                "saran": [
                    "1) Coba DFU/Recovery restore via iTunes/Finder.",
                    "2) Periksa error code saat restore; jika gagal → periksa NAND/eMMC dan jalur boot.",
                    "3) Reball/replace NAND kalau teridentifikasi hardware failure."
                ]
            },
            "Boot loop": {
                "diagnosa": [
                    "Kerusakan firmware, update gagal, atau hardware seperti PMIC/NAND bermasalah."
                ],
                "saran": [
                    "1) Coba DFU/restore firmware.",
                    "2) Jika tetap loop, baca panic-full log untuk indikasi komponen yang bermasalah.",
                    "3) Periksa PMIC & NAND (reflow/reball jika perlu)."
                ]
            },
            "Error panic full log": {
                "diagnosa": [
                    "Kernel panic akibat driver/hardware crash (sensor/PMIC/CPU)."
                ],
                "saran": [
                    "1) Analisa panic-full log: catat missing sensors, thermalmonitord, userspace watchdog.",
                    "2) Prioritaskan pemeriksaan sensor / IC yang disebut di log.",
                    "3) Lakukan test hardware (battery test, dock flex, camera flex, continuity I2C ke PMIC)."
                ]
            }
        }
    },

    # ============================
    # ANDROID DB (lengkap namun disesuaikan)
    # ============================
    "Android": {
        "Daya & Charging": {
            "Tidak bisa di-charge": {
                "diagnosa": [
                    "IC charging (PMIC/charging controller) rusak.",
                    "Port USB-C / MicroUSB kotor / pin patah.",
                    "Baterai drop / connector baterai bermasalah."
                ],
                "saran": [
                    "1) Coba charger & kabel lain (original jika tersedia).",
                    "2) Bersihkan port & periksa pin yang bengkok/terbakar.",
                    "3) Ukur VBUS & VBAT; periksa regulator.",
                    "4) Jika ada tegangan namun tidak charge → kemungkinan IC charging; rework/replace."
                ]
            },
            "Cepat habis baterai": {
                "diagnosa": [
                    "Battery health drop, aplikasi background boros, atau short hardware."
                ],
                "saran": [
                    "1) Periksa battery usage di settings.",
                    "2) Test dengan battery replacement.",
                    "3) Ukur arus standby."
                ]
            },
            "Overheating saat charge": {
                "diagnosa": [
                    "Battery overheating, IC charging bermasalah atau short lokal."
                ],
                "saran": [
                    "1) Stop charging, biarkan device dingin.",
                    "2) Periksa baterai & IC charging.",
                    "3) Reflow/replace IC bila perlu."
                ]
            },
            "Deteksi 'aksesori tidak didukung'": {
                "diagnosa": [
                    "Port/ID resistor tidak sesuai, kabel non-standard, atau firmware memblokir."
                ],
                "saran": [
                    "1) Gunakan kabel berkualitas, test di device lain.",
                    "2) Bersihkan port, periksa jalur resistor ID."
                ]
            }
        },

        "Layar & Display": {
            "Layar blank tapi ada suara": {
                "diagnosa": ["Backlight IC atau konektor LCD bermasalah", "Panel display rusak"],
                "saran": ["Swap panel", "Periksa tegangan backlight", "Periksa konektor FPC"]
            },
            "Layar bergaris / flicker": {
                "diagnosa": ["Panel rusak", "IC display bermasalah"],
                "saran": ["Swap panel", "Reball/replace IC display"]
            },
            "Ghost touch": {
                "diagnosa": ["Panel aftermarket", "IC touch rusak", "Jalur noise"],
                "saran": ["Ganti panel original", "Periksa ground/noise pada jalur touch"]
            }
        },

        "Audio": {
            "Mic tidak berfungsi": {
                "diagnosa": ["Flex mic rusak", "IC audio bermasalah"],
                "saran": ["Ganti mic", "Cek jalur mic ke IC audio"]
            },
            "Speaker kecil / pecah": {
                "diagnosa": ["Speaker rusak", "IC audio bermasalah"],
                "saran": ["Ganti speaker", "Periksa amp/audio IC"]
            },
            "Tidak ada suara saat panggilan": {
                "diagnosa": ["Routing audio salah (software) atau ear speaker rusak"],
                "saran": ["Test speaker, cek routing audio di software, periksa IC audio"]
            }
        },

        "Kamera": {
            "Kamera belakang tidak terdeteksi": {
                "diagnosa": ["Flex kamera putus", "Modul kamera rusak", "Driver kamera corrupt"],
                "saran": ["Swap modul kamera", "Periksa konektor dan jalur", "Update/restore firmware jika perlu"]
            },
            "Kamera depan buram": {
                "diagnosa": ["Lensa kotor", "Modul kamera rusak"],
                "saran": ["Bersihkan lensa", "Ganti modul kamera"]
            },
            "Flash tidak berfungsi": {
                "diagnosa": ["LED flash rusak", "Jalur VCC flash terputus"],
                "saran": ["Ukur tegangan flash", "Ganti modul flash atau periksa jalur"]
            }
        },

        "Sinyal & Koneksi": {
            "Tidak ada layanan / searching terus": {
                "diagnosa": ["Baseband / modem corrupt", "Antenna atau PA bermasalah"],
                "saran": ["Periksa IMEI, cek jalur antena, reflash modem/baseband"]
            },
            "IMEI hilang": {
                "diagnosa": ["EFS/NVRAM corrupt", "Baseband firmware error"],
                "saran": ["Restore EFS backup, gunakan tools service untuk repair IMEI"]
            },
            "WiFi abu-abu / tidak bisa diaktifkan": {
                "diagnosa": ["IC WiFi corrupt", "Firmware error"],
                "saran": ["Reflash firmware, reball/replace IC WiFi"]
            },
            "Bluetooth tidak jalan": {
                "diagnosa": ["IC BT/WiFi corrupt", "Firmware issues"],
                "saran": ["Reset BT settings, reflash firmware, replace IC if needed"]
            }
        },

        "Sensor": {
            "Proximity sensor tidak jalan": {
                "diagnosa": ["Sensor/proximity flex rusak", "Konektor putus"],
                "saran": ["Ganti/cek flex sensor, cek konektor"]
            },
            "Gyroscope error": {
                "diagnosa": ["IC sensor bermasalah", "Kalibrasi error"],
                "saran": ["Kalibrasi ulang, reball/replace IC sensor"]
            }
        },

        "Software & Boot": {
            "Stuck logo / bootloop": {
                "diagnosa": ["System corrupt", "eMMC/NAND error"],
                "saran": ["Reflash firmware, jika gagal periksa eMMC/NAND"]
            },
            "Restore iTunes gagal": {
                "diagnosa": ["Kesalahan komunikasi tool", "eMMC corrupt"],
                "saran": ["Coba PC lain, cek kabel & port, periksa eMMC"]
            }
        },

        "Lainnya": {
            "Getar tidak berfungsi": {
                "diagnosa": ["Motor getar rusak", "Driver IC bermasalah"],
                "saran": ["Ganti motor getar, cek jalur driver"]
            },
            "NFC mati": {
                "diagnosa": ["IC NFC rusak", "Antenna NFC putus"],
                "saran": ["Cek jalur NFC, reball/replace IC NFC"]
            },
            "GPS tidak akurat": {
                "diagnosa": ["Antenna GPS bermasalah", "IC RF error"],
                "saran": ["Cek antenna GPS, reball/replace IC RF"]
            },
            "Tidak bisa update iOS / OTA": {
                "diagnosa": ["Partition corrupt", "eMMC/NAND problem", "Network issue"],
                "saran": ["Cek log update, coba manual update via iTunes, periksa storage hardware"]
            }
        }
    }
}

# ============================
# Helper: build report text & PDF
# ============================
def build_report(platform, category, symptom, entry):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = []
    lines.append("="*68)
    lines.append("🔧 DokterHP v1 By IDT")
    lines.append("Asisten Diagnosa & Saran Perbaikan HP (iPhone & Android)")
    lines.append("="*68)
    lines.append(f"Waktu    : {now}")
    lines.append(f"Platform : {platform}")
    lines.append(f"Kategori : {category}")
    lines.append(f"Gejala   : {symptom}")
    lines.append("")
    lines.append("🩺 Diagnosa kemungkinan:")
    for idx, d in enumerate(entry.get("diagnosa", []), start=1):
        lines.append(f"  {idx}. {d}")
    lines.append("")
    lines.append("🛠️ Saran Perbaikan (langkah by step):")
    for idx, s in enumerate(entry.get("saran", []), start=1):
        lines.append(f"  {idx}. {s}")
    lines.append("")
    lines.append("Catatan:")
    lines.append(" - Panduan awal berdasarkan gejala. Untuk diagnosis pasti, lakukan pemeriksaan hardware/alat.")
    lines.append(" - Jika tersedia panic-full / kernel log, analisa untuk petunjuk komponen terkait.")
    lines.append("="*68)
    return "\n".join(lines)

def export_pdf_bytes(report_text):
    buffer = io.BytesIO()
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    for line in report_text.split("\n"):
        if line.strip() == "":
            story.append(Spacer(1,6))
        else:
            wrapped = textwrap.fill(line, width=100)
            story.append(Paragraph(wrapped, styles["Normal"]))
            story.append(Spacer(1,4))
    doc.build(story)
    buffer.seek(0)
    return buffer

# ============================
# Streamlit UI logic
# ============================
col1, col2 = st.columns([1, 2])
with col1:
    st.write("**Pilih Platform & Gejala**")
    platform = st.selectbox("Platform", list(DB.keys()))
    category = st.selectbox("Kategori", list(DB[platform].keys()))
    symptom = st.selectbox("Gejala", list(DB[platform][category].keys()))
    st.write("")
    if st.button("🔍 Jalankan Diagnosa"):
        entry = DB[platform][category][symptom]
        report = build_report(platform, category, symptom, entry)
        st.session_state["current_report"] = report
        st.rerun()  # rerun to show result area (simple way)

with col2:
    st.write("**Hasil Diagnosa & Saran**")
    report_text = st.session_state.get("current_report", "")
    if report_text:
        st.text_area("📋 Laporan Diagnosa", value=report_text, height=520)
        # Download TXT
        st.download_button("💾 Download TXT", report_text, file_name="dokterhp_diagnosa.txt", mime="text/plain")
        # Download PDF
        pdf_buffer = export_pdf_bytes(report_text)
        st.download_button("📄 Download PDF", pdf_buffer, file_name="dokterhp_diagnosa.pdf", mime="application/pdf")
    else:
        st.info("Pilih Platform → Kategori → Gejala lalu klik 'Jalankan Diagnosa'.")

st.write("---")
st.markdown("**Copyright © DokterHP v1 By IDT** · interested in collaboration @maxxjen1 on instagram", unsafe_allow_html=True)
st.caption("Disclaimer: Hasil diagnostik adalah panduan awal. Untuk perbaikan hardware, lakukan pemeriksaan teknis dengan alat yang sesuai.")


