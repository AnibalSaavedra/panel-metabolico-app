
import streamlit as st
from fpdf import FPDF
import datetime
import os

def calcular_indices(datos):
    comentarios = []
    resultados = {}

    try:
        colesterol = float(datos["Colesterol"])
        hdl = float(datos["HDL"])
        ldl = float(datos["LDL"])
        trig = float(datos["Triglicéridos"])
        glucosa = float(datos["Glucosa"])
        insulina = float(datos["Insulina"])
    except:
        return None, None, "Error: Verifica que todos los valores sean numéricos."

    castelli = round(colesterol / hdl, 2) if hdl != 0 else 0
    resultados["Índice de Castelli"] = castelli
    if castelli > 4.5:
        comentarios.append("Índice de Castelli elevado: riesgo cardiovascular aumentado.")

    ldl_hdl = round(ldl / hdl, 2) if hdl != 0 else 0
    resultados["Índice LDL/HDL"] = ldl_hdl
    if ldl_hdl > 3.5:
        comentarios.append("Relación LDL/HDL elevada: riesgo cardiovascular aumentado.")

    trig_hdl = round(trig / hdl, 2) if hdl != 0 else 0
    resultados["Índice Triglicéridos/HDL"] = trig_hdl
    if trig_hdl > 3.0:
        comentarios.append("Índice Triglicéridos/HDL elevado: sospecha de resistencia a la insulina.")

    homa_ir = round((glucosa * insulina) / 405, 2)
    resultados["HOMA-IR"] = homa_ir
    if homa_ir >= 2.5:
        comentarios.append("HOMA-IR elevado: posible resistencia a la insulina.")

    return resultados, comentarios, None

def generar_pdf(datos, bioquimicos, indices, interpretacion, constantes, extra):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "INFORME PANEL METABÓLICO EXTENDIDO", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    for campo in ["Nombre paciente", "RUT", "Fecha toma muestra", "Hora toma muestra", "Laboratorio", "Validador"]:
        pdf.cell(0, 10, f"{campo}: {datos[campo]}", ln=True)

    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    pdf.cell(0, 10, f"Fecha/Hora de emisión: {now}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Resultados Bioquímicos:", ln=True)
    pdf.set_font("Arial", size=12)
    for k, v in bioquimicos.items():
        pdf.cell(0, 10, f"{k}: {v}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Índices Metabólicos:", ln=True)
    pdf.set_font("Arial", size=12)
    for k, v in indices.items():
        pdf.cell(0, 10, f"{k}: {v}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Interpretación Clínica:", ln=True)
    pdf.set_font("Arial", size=12)
    for linea in interpretacion:
        pdf.multi_cell(0, 10, linea)

    if constantes.strip():
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Constantes Vitales:", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, constantes.strip())

    if extra.strip():
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Exámenes Complementarios:", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, extra.strip())

    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Validador: {datos['Validador']}", ln=True)

    nombre_archivo = f"panel_metabolico_{datos['Nombre paciente'].replace(' ', '_')}.pdf"
    pdf.output(nombre_archivo)
    return nombre_archivo

st.title("🧪 Panel Metabólico Extendido - Decreto 20")

with st.form("formulario"):
    datos = {
        "Nombre paciente": st.text_input("Nombre paciente"),
        "RUT": st.text_input("RUT"),
        "Fecha toma muestra": st.text_input("Fecha toma muestra (dd/mm/aaaa)"),
        "Hora toma muestra": st.text_input("Hora toma muestra (HH:MM)"),
        "Laboratorio": st.text_input("Laboratorio"),
        "Validador": st.text_input("Validador (nombre y cargo)")
    }

    st.markdown("### Valores Bioquímicos")
    colesterol = st.text_input("Colesterol Total (mg/dL)")
    hdl = st.text_input("HDL (mg/dL)")
    ldl = st.text_input("LDL (mg/dL)")
    trig = st.text_input("Triglicéridos (mg/dL)")
    glucosa = st.text_input("Glucosa (mg/dL)")
    insulina = st.text_input("Insulina (uU/mL)")

    constantes = st.text_area("Constantes Vitales")
    extra = st.text_area("Exámenes Complementarios")

    submit = st.form_submit_button("Generar Informe")

if submit:
    try:
        valores = {
            "Colesterol": float(colesterol.replace(",", ".")),
            "HDL": float(hdl.replace(",", ".")),
            "LDL": float(ldl.replace(",", ".")),
            "Triglicéridos": float(trig.replace(",", ".")),
            "Glucosa": float(glucosa.replace(",", ".")),
            "Insulina": float(insulina.replace(",", "."))
        }

        bioquimicos = {
            "Colesterol Total (mg/dL)": colesterol,
            "HDL (mg/dL)": hdl,
            "LDL (mg/dL)": ldl,
            "Triglicéridos (mg/dL)": trig,
            "Glucosa (mg/dL)": glucosa,
            "Insulina (uU/mL)": insulina
        }

        indices, comentarios, error = calcular_indices(valores)
        if error:
            st.error(error)
        else:
            archivo = generar_pdf(datos, bioquimicos, indices, comentarios, constantes, extra)
            with open(archivo, "rb") as f:
                st.download_button("📄 Descargar Informe PDF", f, file_name=archivo, mime="application/pdf")
            st.success("Informe generado correctamente.")

    except Exception as e:
        st.error(f"Error: {e}")
