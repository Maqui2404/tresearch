import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
import tempfile

# Clase personalizada para agregar encabezado y pie de página
class PDF(FPDF):
    def header(self):
        # Establecer fuente para el encabezado
        self.set_font("Arial", "B", 10)
        # Encabezado (se repite en todas las páginas)
        self.cell(0, 10, "Informe de Prueba t de Student de la app hecha por estudiantes de la Universidad Nacional del Altiplano de", ln=True, align="C")
        self.ln(5)  # Espacio extra después del encabezado

    def footer(self):
        # Establecer posición del pie de página a 1.5 cm del final
        self.set_y(-15)
        # Establecer fuente para el pie de página
        self.set_font("Arial", "I", 8)
        # Número de página
        self.cell(0, 10, f"Página {self.page_no()}", 0, 0, "C")

# Título y descripción de la aplicación
st.title("Aplicación de Prueba t de Student")
st.write("""
Esta aplicación permite realizar pruebas t de Student para comparar las medias de dos grupos o para comparar la media de un grupo con un valor teórico.
Puedes cargar tus datos, seleccionar las variables y realizar la prueba de forma interactiva.
""")

# Carga de datos
uploaded_file = st.file_uploader("Cargar archivo CSV o Excel", type=["csv", "xlsx"])
if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    st.write("Datos cargados:")
    st.dataframe(df.head())

    # Selección de variables
    st.write("### Selección de Variables")
    columns = df.select_dtypes(include=np.number).columns.tolist()
    test_type = st.radio("Tipo de Prueba t", ["Dos muestras independientes", "Una muestra", "Muestras emparejadas"])

    if test_type == "Dos muestras independientes":
        variable1 = st.selectbox("Selecciona la primera variable numérica", columns)
        variable2 = st.selectbox("Selecciona la segunda variable numérica", [col for col in columns if col != variable1])
        equal_var = st.checkbox("¿Asumir varianzas iguales?", value=True)
        t_stat, p_value = stats.ttest_ind(df[variable1], df[variable2], equal_var=equal_var)
        st.write(f"Resultados de la Prueba t de Dos Muestras Independientes:")
        st.write(f"t-statistic: {t_stat:.4f}")
        st.write(f"p-value: {p_value:.4f}")
        st.write(f"Grados de libertad: {len(df[variable1]) + len(df[variable2]) - 2}")
        
        # Gráfico de comparación
        st.write("### Visualización Gráfica")
        fig1, ax1 = plt.subplots()
        sns.boxplot(data=df[[variable1, variable2]], ax=ax1)
        st.pyplot(fig1)

        # Histograma de las variables
        st.write("### Histogramas")
        fig2, (ax2, ax3) = plt.subplots(1, 2, figsize=(10, 4))
        sns.histplot(df[variable1], kde=True, ax=ax2)
        ax2.set_title(f'Histograma de {variable1}')
        sns.histplot(df[variable2], kde=True, ax=ax3)
        ax3.set_title(f'Histograma de {variable2}')
        st.pyplot(fig2)

        # Gráfico de dispersión
        st.write("### Gráfico de Dispersión")
        fig3, ax4 = plt.subplots()
        sns.scatterplot(x=df[variable1], y=df[variable2], ax=ax4)
        ax4.set_title(f'Dispersión entre {variable1} y {variable2}')
        st.pyplot(fig3)
    
    elif test_type == "Una muestra":
        variable = st.selectbox("Selecciona la variable numérica", columns)
        test_value = st.number_input("Ingresa el valor teórico para comparar", value=0.0)
        t_stat, p_value = stats.ttest_1samp(df[variable], test_value)
        st.write(f"Resultados de la Prueba t de Una Muestra:")
        st.write(f"t-statistic: {t_stat:.4f}")
        st.write(f"p-value: {p_value:.4f}")
        st.write(f"Grados de libertad: {len(df[variable]) - 1}")

        # Histograma de la variable
        st.write("### Histograma")
        fig4, ax5 = plt.subplots()
        sns.histplot(df[variable], kde=True, ax=ax5)
        ax5.set_title(f'Histograma de {variable}')
        st.pyplot(fig4)

    elif test_type == "Muestras emparejadas":
        variable1 = st.selectbox("Selecciona la primera variable numérica", columns)
        variable2 = st.selectbox("Selecciona la segunda variable numérica", [col for col in columns if col != variable1])
        t_stat, p_value = stats.ttest_rel(df[variable1], df[variable2])
        st.write(f"Resultados de la Prueba t de Muestras Emparejadas:")
        st.write(f"t-statistic: {t_stat:.4f}")
        st.write(f"p-value: {p_value:.4f}")
        st.write(f"Grados de libertad: {len(df[variable1]) - 1}")

        # Gráfico de comparación
        st.write("### Visualización Gráfica")
        fig1, ax1 = plt.subplots()
        sns.boxplot(data=df[[variable1, variable2]], ax=ax1)
        st.pyplot(fig1)

        # Histograma de las variables
        st.write("### Histogramas")
        fig2, (ax2, ax3) = plt.subplots(1, 2, figsize=(10, 4))
        sns.histplot(df[variable1], kde=True, ax=ax2)
        ax2.set_title(f'Histograma de {variable1}')
        sns.histplot(df[variable2], kde=True, ax=ax3)
        ax3.set_title(f'Histograma de {variable2}')
        st.pyplot(fig2)

    # Interpretación de resultados
    st.write("### Interpretación de Resultados")
    alpha = st.number_input("Nivel de significancia (alpha)", value=0.05)
    interpretacion = ("Rechazamos la hipótesis nula. Existe una diferencia significativa."
                      if p_value < alpha else
                      "No podemos rechazar la hipótesis nula. No existe evidencia suficiente para afirmar que hay una diferencia significativa.")
    st.write(interpretacion)

    # Generar reporte
    reporte = f"""
    Resultados de la Prueba t de Student\n
    Tipo de prueba: {test_type}\n
    t-statistic: {t_stat:.4f}\n
    p-value: {p_value:.4f}\n
    Nivel de significancia (alpha): {alpha}\n
    Interpretación: {interpretacion}
    """

    # Descargar reporte en texto
    st.download_button(
        label="Descargar Reporte (Texto)",
        data=reporte,
        file_name='reporte_prueba_t.txt',
        mime='text/plain'
    )

    # Opción para generar PDF
    if st.button("Generar Informe en PDF"):
        pdf = PDF()  # Usar la clase personalizada con encabezado y pie de página
        pdf.add_page()

        # Título (solo en la primera página)
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Resultados de la Prueba t de Student", ln=True, align="C")
        pdf.ln(10)

        # Resultados
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, reporte)

        # Gráfico de comparación
        pdf.ln(10)
        pdf.cell(200, 10, txt="Gráficos:", ln=True, align='C')

        # Guardar los gráficos en archivos temporales y luego insertarlos en el PDF
        if test_type == "Dos muestras independientes":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile1:
                fig1.savefig(tmpfile1.name, format="png")
                pdf.image(tmpfile1.name, x=10, y=None, w=180)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile2:
                fig2.savefig(tmpfile2.name, format="png")
                pdf.add_page()
                pdf.image(tmpfile2.name, x=10, y=None, w=180)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile3:
                fig3.savefig(tmpfile3.name, format="png")
                pdf.add_page()
                pdf.image(tmpfile3.name, x=10, y=None, w=180)

        elif test_type == "Una muestra":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile4:
                fig4.savefig(tmpfile4.name, format="png")
                pdf.image(tmpfile4.name, x=10, y=None, w=180)

        elif test_type == "Muestras emparejadas":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile1:
                fig1.savefig(tmpfile1.name, format="png")
                pdf.image(tmpfile1.name, x=10, y=None, w=180)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile2:
                fig2.savefig(tmpfile2.name, format="png")
                pdf.add_page()
                pdf.image(tmpfile2.name, x=10, y=None, w=180)

        # Guardar el archivo PDF en un buffer
        pdf_buffer = BytesIO()
        pdf_output = pdf.output(dest='S').encode('latin1')
        pdf_buffer.write(pdf_output)
        pdf_buffer.seek(0)

        # Descargar el archivo PDF
        st.download_button(
            label="Descargar Informe en PDF",
            data=pdf_buffer,
            file_name="informe_prueba_t.pdf",
            mime="application/pdf"
        )



else:
    st.write("Por favor, carga un archivo de datos para comenzar.")
