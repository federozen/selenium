import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Diccionario con la configuración de cada medio
media_sources = {
    "Clarin": {
        "url": "https://www.clarin.com/deportes",
        "xpath": "//ul/li/article/div/a",
        "headline_attr": "aria-label",  # Titular en el atributo aria-label
        "link_attr": "href",         # Extraer enlace
        "base_url": "https://www.clarin.com"  # Para URLs relativas
    },
    "La Nacion": {
        "url": "https://www.lanacion.com.ar/deportes/",
        "xpath": "//h2[contains(@class, 'com-title')]",  # Ajusta según la estructura actual
        "headline_attr": "text",      # Se extrae el texto visible
        "link_attr": "",          # No se extrae enlace en este ejemplo
        "base_url": ""
    },
    "Infobae": {
        "url": "https://www.infobae.com/deportes/",
        "xpath": "//h2",          # XPath para titulares (ajustar si es necesario)
        "headline_attr": "text",      # Se extrae el texto visible
        "link_attr": "",
        "base_url": ""
    },
    "ESPN": {
        "url": "https://www.espn.com.ar/",
        # Utilizamos una unión de etiquetas h1 y h2 para capturar titulares (ajusta si es necesario)
        "xpath": "//h1 | //h2",
        "headline_attr": "text",
        "link_attr": "",
        "base_url": ""
    },
    "Ole": {
        "url": "https://www.ole.com.ar/",
        # XPath basado en ejemplo previo (ajusta según la estructura actual del sitio)
        "xpath": "//h2[contains(@class, 'sc-fa18824-3')]",
        "headline_attr": "text",
        "link_attr": "",
        "base_url": ""
    }
}

@st.cache_data
def scrape_headlines():
    """
    Función para extraer titulares de noticias deportivas de varios medios usando Selenium.
    Retorna un DataFrame de Pandas con los resultados.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Ejecuta sin abrir el navegador
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    data = []  # Lista para almacenar los datos extraídos

    for source, config in media_sources.items():
        print(f"Scraping {source}...") # Esto se verá en la consola, no en Streamlit
        driver.get(config["url"])

        # Esperar a que se carguen los elementos especificados por el XPath
        wait = WebDriverWait(driver, 10)
        try:
            elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, config["xpath"])))
        except Exception as e:
            print(f"Error en {source}: {e}") # Esto se verá en la consola, no en Streamlit
            continue

        for el in elements:
            # Extraer el titular: si headline_attr es "text", se utiliza el texto visible
            if config["headline_attr"] == "text":
                headline = el.text.strip()
            else:
                headline = el.get_attribute(config["headline_attr"])
                headline = headline.strip() if headline else ""

            if not headline:
                continue  # Omitir si no se encontró titular

            # Extraer enlace si se definió link_attr
            link = ""
            if config["link_attr"]:
                link = el.get_attribute(config["link_attr"])
                if link and config.get("base_url", "") and link.startswith("/"):
                    link = config["base_url"] + link

            data.append({
                "Source": source,
                "Titular": headline,
                "URL": link
            })

    # Cerrar el navegador
    driver.quit()
    df = pd.DataFrame(data)
    return df

st.title("Titulares Deportivos de Argentina")

if st.button("Obtener Titulares"):
    with st.spinner("Scrapeando titulares..."):
        titulares_df = scrape_headlines()

    if not titulares_df.empty:
        st.success("¡Titulares obtenidos!")
        # **MODIFICACIÓN IMPORTANTE: Mostrar titulares como texto**
        for index, row in titulares_df.iterrows():
            st.markdown(f"**Fuente:** {row['Source']}") # Fuente en negrita
            st.write(f"**Titular:** {row['Titular']}")   # Titular normal
            if row['URL']: # Mostrar enlace si existe
                st.write(f"[Leer más...]({row['URL']})") # Enlace como texto "Leer más..."
            st.write("---") # Separador visual entre titulares

    else:
        st.error("No se pudieron obtener los titulares. Revisa la consola para más detalles.")