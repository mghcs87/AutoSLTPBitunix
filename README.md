### Stop Loss y Take Profit Automático para Futuros de Bitunix

Este script fue desarrollado para proteger y optimizar tus operaciones en los mercados de futuros de **Bitunix**. Te permite configurar dos parámetros clave:

* **Stop Loss:** Define el monto máximo en dólares que estás dispuesto a perder en una operación (ej. `10`).
* **Take Profit (Opcional):** Define el porcentaje de ganancia con el que deseas cerrar automáticamente tu posición para asegurar beneficios (ej. `1%`).

**NOTA:** Este script está diseñado para operar con pares **USDT**.

---

### Aclaración Importante

Este script es una versión adaptada para el exchange **Bitunix**, basada en los scripts originales de Stop Loss y Take Profit de **@ElGafasTrading**. Está diseñado principalmente para la operativa de Cardiaco.

Para más información, estrategias o dudas sobre el concepto original, te recomendamos visitar directamente al creador en sus redes:

* **Twitter:** [@ElGafasTrading](https://twitter.com/ElGafasTrading)
* **Instagram:** [elgafastrading](https://www.instagram.com/elgafastrading/)
* **Youtube:** [ElGafasTrading](https://www.youtube.com/@ElGafasTrading)

---

### ¿Cómo usar el script? ⚙️

1.  **Descargar Python**
    * Si aún no lo tienes, instálalo desde [python.org](https://www.python.org/).

2.  **Clonar o descargar el proyecto**
    * Descarga los archivos a tu computadora.

3.  **Instalar la librería necesaria**
    * Abre una terminal (CMD, PowerShell, etc.) y ejecuta el siguiente comando para instalar la librería necesaria:
        ```bash
        pip install -r requirements.txt
        ```

4.  **Configurar tus claves de API**
    * Modifica el archivo `config.yaml` con un editor de texto como [Sublime Text](https://www.sublimetext.com/) o el bloc de notas.
    * Agrega tu **API KEY** y tu **API SECRET**. Puedes obtenerlas desde tu panel de usuario en Bitunix.
        ```yaml
        api_key: TU_API_KEY_DE_BITUNIX
        secret_key: TU_API_SECRET_DE_BITUNIX
        ```

5.  **Ejecutar el script**
    * Guarda los cambios en `config.yaml` y ejecuta el script desde tu terminal con el siguiente comando:
        ```bash
        python script.py
        ```

**IMPORTANTE:** Para un funcionamiento correcto, asegúrate de que tu cuenta de futuros en Bitunix NO esté en "Hedge Mode" (Modo Cobertura).

---

### Advertencia de Riesgo ⚠️

Los mercados de futuros de criptomonedas son extremadamente volátiles y conllevan un alto riesgo. El uso de este script debe hacerse con un sólido conocimiento de los riesgos asociados al trading.

El autor de esta adaptación no se hace responsable de ninguna pérdida financiera, directa o indirecta, que pueda resultar del uso de este software. **Utilízalo bajo tu propia responsabilidad.**
