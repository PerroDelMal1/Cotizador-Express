import os
import json
import datetime
import urllib.parse
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import AsyncImage

# Importación segura para Android / Escritorio
from kivy.utils import platform
if platform == 'android':
    from jnius import autoclass
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Intent = autoclass('android.content.Intent')
    StringClass = autoclass('java.lang.String')
else:
    import webbrowser


from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def obtener_ruta_descargas():
    ruta_publica = "/storage/emulated/0/Download"
    try:
        if os.path.exists(ruta_publica):
            return ruta_publica
    except Exception:
        pass
    return os.path.expanduser("~")


TEXTOS = {
    "ES": {
        "app_title": "Cotizador Express PRO",
        "header": "PRESUPUESTO / COTIZACION",
        "trato": "Estimado(a)",
        "trato_defecto": "Estimado(a) Señor / Señora",
        "nombre_emisor_hint": "Tu Nombre / Empresa (Emisor)",
        "tel_emisor_hint": "Tu Teléfono / WhatsApp",
        "proyecto": "Proyecto:",
        "pro_hint": "Nombre del Proyecto *",
        "servicio": "Servicio a Realizar:",
        "ser_hint": "Servicio a Realizar (Detalle)",
        "servicio_defecto": "Servicio técnico estándar.",
        "garantia": "Garantía del Servicio:",
        "garantia_txt": "sobre la labor realizada.",
        "garantia_lbl": "Garantía del Servicio:",
        "mat": "Costo de Materiales (Global)",
        "mat_hint": "Monto Total Materiales ($)",
        "mat_sub": "Subtotal Materiales",
        "mo": "Mano de Obra",
        "mo_hint": "Mano de Obra ($)",
        "mo_det_hint": "Detalle Mano de Obra (Opcional)",
        "total": "TOTAL ESTIMADO",
        "hdr_cant": "Cant.",
        "hdr_item": "Ítem",
        "hdr_costo": "Costo ($)",
        "btn_add_mat": "+ Agregar Ítem Detallado",
        "btn_plazo": "Plazo de Ejecución (Para el PDF)",
        "lbl_f_ini": "Fecha de Inicio:",
        "lbl_f_fin": "Fecha de Término (Opcional):",
        "btn_pdf": "GENERAR PDF",
        "btn_agenda": "GUARDAR EN AGENDA PRO",
        "btn_actualizar": "ACTUALIZAR OBRA EN AGENDA",
        "agenda_title": "Mi Agenda PRO (Panel de Control)",
        "perfil_title": "Perfil Profesional / Empresa",
        "tab_obras": "Obras",
        "tab_bitacoras": "Bitácoras",
        "tab_notas": "Notas",
        "filtro_todos": "Todos",
        "filtro_pendiente": "Pendiente",
        "filtro_en_ejecucion": "En Ejecución",
        "filtro_finalizado": "Finalizado",
        "card_edit": "Editar",
        "card_copy": "Duplicar",
        "card_del": "Borrar",
        "msg_no_proyectos": "No hay proyectos en este filtro.",
        "lbl_fecha_card": "Fecha:",
        "opcion_a_lbl": "Opción A: Materiales Globales (Solo Valor)",
        "opcion_b_lbl": "O bien, Opción B: Detallar Materiales Ítem por Ítem",
        "privacy_title": "Política de Privacidad y Términos",
        "privacy_desc": "Esta aplicación almacena datos de forma local en su dispositivo para el funcionamiento de la agenda y generación de PDFs. Ningún dato personal es compartido con terceros."
    },
    "EN": {
        "app_title": "Express Quotation PRO",
        "header": "SERVICE QUOTATION",
        "trato": "Dear",
        "trato_defecto": "Dear Customer",
        "nombre_emisor_hint": "Your Name / Company (Issuer)",
        "tel_emisor_hint": "Your Phone / WhatsApp",
        "project": "Project:",
        "pro_hint": "Project Name *",
        "servicio": "Service Scope:",
        "ser_hint": "Service Details",
        "servicio_defecto": "Standard technical service.",
        "garantia": "Service Warranty:",
        "garantia_txt": "coverage on performed labor.",
        "garantia_lbl": "Service Warranty:",
        "mat": "Materials Cost (Global)",
        "mat_hint": "Total Materials Amount ($)",
        "mat_sub": "Materials Subtotal",
        "mo": "Labor Cost",
        "mo_hint": "Labor ($)",
        "mo_det_hint": "Labor Details (Optional)",
        "total": "ESTIMATED TOTAL",
        "hdr_cant": "Qty",
        "hdr_item": "Item",
        "hdr_costo": "Cost ($)",
        "btn_add_mat": "+ Add Detailed Item",
        "btn_plazo": "Execution Term (For PDF)",
        "lbl_f_ini": "Start Date:",
        "lbl_f_fin": "End Date (Optional):",
        "btn_pdf": "GENERATE PDF",
        "btn_agenda": "SAVE IN AGENDA PRO",
        "btn_actualizar": "UPDATE PROJECT IN AGENDA",
        "agenda_title": "My Agenda PRO (Control Panel)",
        "perfil_title": "Professional / Company Profile",
        "tab_obras": "Projects",
        "tab_bitacoras": "Logs",
        "tab_notas": "Notes",
        "filtro_todos": "All",
        "filtro_pendiente": "Pending",
        "filtro_en_ejecucion": "In Progress",
        "filtro_finalizado": "Completed",
        "card_edit": "Edit",
        "card_copy": "Copy",
        "card_del": "Del",
        "msg_no_proyectos": "No projects found under this filter.",
        "lbl_fecha_card": "Date:",
        "opcion_a_lbl": "Option A: Global Materials (Value Only)",
        "opcion_b_lbl": "Or Option B: Detail Materials Item by Item",
        "privacy_title": "Privacy Policy & Terms",
        "privacy_desc": "This application stores data locally on your device for agenda management and PDF generation. No personal data is shared with third parties."
    }
}


def crear_pdf_completo(filename, nombre_emisor, telefono_emisor, proyecto, servicio, mat_costo_global, mo_costo, mo_detalle, garantia, usar_detallado, materiales_lista, idioma_code="ES", f_inicio="", f_termino="", perfil_data=None):
    carpeta = obtener_ruta_descargas()
    filepath = os.path.join(carpeta, filename)


    doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()


    t_lang = TEXTOS.get(idioma_code, TEXTOS["ES"])
    trato_cliente = t_lang['trato_defecto']


    titulo_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor("#1A252F"), spaceAfter=15)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor("#2C3E50"))
    bold_style = ParagraphStyle('Bold', parent=body_style, fontName='Helvetica-Bold')

    tiene_perfil = perfil_data and perfil_data.get("nombre", "").strip()
    if tiene_perfil:
        p_nom = perfil_data.get("nombre", "")
        p_tel = perfil_data.get("telefono", "")
        p_corr = perfil_data.get("correo", "")
        p_ext = perfil_data.get("extra", "")
        
        corp_txt = f"<b>{p_nom}</b><br/>"
        if p_tel: corp_txt += f"Teléfono / WhatsApp: {p_tel}<br/>"
        if p_corr: corp_txt += f"Correo: {p_corr}<br/>"
        if p_ext: corp_txt += f"{p_ext}<br/>"
        
        story.append(Paragraph(corp_txt, body_style))
        story.append(Spacer(1, 10))
    else:
        nom_final = nombre_emisor.strip() if nombre_emisor and nombre_emisor.strip() else ("Mi Empresa / Servicio" if idioma_code=="ES" else "My Company")
        tel_final = telefono_emisor.strip() if telefono_emisor else ""
        
        corp_txt = f"<b>{nom_final}</b><br/>"
        if tel_final: corp_txt += f"Teléfono / WhatsApp: {tel_final}<br/>"
        
        story.append(Paragraph(corp_txt, body_style))
        story.append(Spacer(1, 10))

    story.append(Paragraph(f"<b>{t_lang['header']}</b>", titulo_style))
    story.append(Spacer(1, 10))


    story.append(Paragraph(f"<b>{trato_cliente}</b>", body_style))
    story.append(Paragraph(f"<b>{t_lang['proyecto']}</b> {proyecto}", body_style))
    
    if f_inicio:
        termino_txt = f_termino if f_termino else ("Por determinar" if idioma_code=="ES" else "TBD")
        lbl_plazo_pdf = "Plazo de Ejecución:" if idioma_code == "ES" else "Execution Term:"
        del_txt = "Del" if idioma_code == "ES" else "From"
        al_txt = "al" if idioma_code == "ES" else "to"
        story.append(Paragraph(f"<b>{lbl_plazo_pdf}</b> {del_txt} {f_inicio} {al_txt} {termino_txt}", body_style))
    
    story.append(Spacer(1, 12))


    story.append(Paragraph(f"<b>{t_lang['servicio']}</b>", bold_style))
    story.append(Paragraph(servicio if servicio and servicio.strip() else t_lang['servicio_defecto'], body_style))
    story.append(Spacer(1, 15))


    try:
        mo_val = int(mo_costo) if mo_costo and str(mo_costo).strip() else 0
    except ValueError:
        mo_val = 0


    mo_detalle_str = str(mo_detalle) if mo_detalle else ""
    if mo_detalle_str.strip():
        mo_celda = Paragraph(f"<b>{t_lang['mo']}</b><br/><font color='#566573' size='9'><i>{mo_detalle_str.strip()}</i></font>", body_style)
    else:
        mo_celda = Paragraph(f"<b>{t_lang['mo']}</b>", body_style)


    data = []
    if usar_detallado and materiales_lista and len(materiales_lista) > 0:
        data.append([Paragraph(f"<b>{t_lang['hdr_cant']}</b>", bold_style), Paragraph(f"<b>{t_lang['hdr_item']}</b>", bold_style), Paragraph(f"<b>{t_lang['hdr_costo']}</b>", bold_style)])
        
        total_mat = 0
        for cant_val, mat_nombre, mat_precio in materiales_lista:
            subtotal_fila = cant_val * mat_precio
            data.append([Paragraph(str(cant_val), body_style), Paragraph(mat_nombre, body_style), f"${subtotal_fila:,.0f}"])
            total_mat += subtotal_fila
            
        data.append([Paragraph(f"<b>{t_lang['mat_sub']}</b>", bold_style), Paragraph("", body_style), f"${total_mat:,.0f}"])
        data.append([mo_celda, Paragraph("", body_style), f"${mo_val:,.0f}"])
        total_general = total_mat + mo_val
        col_widths = [50, 290, 160]
    else:
        try:
            mat_val = int(mat_costo_global) if mat_costo_global and str(mat_costo_global).strip() else 0
        except ValueError:
            mat_val = 0
        data = [
            [Paragraph(f"<b>{t_lang['mat']}</b>", body_style), f"${mat_val:,.0f}"],
            [mo_celda, f"${mo_val:,.0f}"]
        ]
        total_general = mat_val + mo_val
        col_widths = [340, 160]


    data.append([Paragraph(f"<b>{t_lang['total']}</b>", ParagraphStyle('TLabel', parent=bold_style, fontSize=11, textColor=colors.HexColor("#27AE60"))),
                 Paragraph(f"<b>${total_general:,.0f} CLP</b>", ParagraphStyle('TVal', parent=bold_style, fontSize=11, textColor=colors.HexColor("#27AE60")))] if not (usar_detallado and materiales_lista) else 
                [Paragraph(f"<b>{t_lang['total']}</b>", ParagraphStyle('TLabel', parent=bold_style, fontSize=11, textColor=colors.HexColor("#27AE60"))), Paragraph("", body_style), Paragraph(f"<b>${total_general:,.0f} CLP</b>", ParagraphStyle('TVal', parent=bold_style, fontSize=11, textColor=colors.HexColor("#27AE60")))])


    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8F9F9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#BDC3C7")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 7),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))


    garantia_str = str(garantia) if garantia else ""
    if garantia_str and garantia_str not in ["Sin Garantia", "No incluir", "No Warranty", ""]:
        txt_gar = f"<b>{t_lang['garantia']}</b> {garantia_str} {t_lang['garantia_txt']}"
        story.append(Paragraph(txt_gar, body_style))
        story.append(Spacer(1, 15))

    doc.build(story)
    return filepath


ANOS_DISPONIBLES = [str(y) for y in range(2026, 2037)]


KV = """
ScreenManager:
    CotizadorScreen:
    AgendaScreen:
    PerfilScreen:

<CotizadorScreen>:
    name: "cotizador"
    md_bg_color: 0.08, 0.08, 0.08, 1

    MDBoxLayout:
        orientation: 'vertical'

        MDTopAppBar:
            id: top_bar
            title: "Cotizador Express PRO"
            elevation: 0
            md_bg_color: 0.12, 0.12, 0.12, 1
            specific_text_color: 0.9, 0.9, 0.9, 1
            left_action_items: [["translate", lambda x: app.cambiar_idioma_siguiente(), "Cambiar Idioma"]]
            right_action_items: [["account", lambda x: app.ir_a_perfil(), "Perfil Profesional"], ["calendar-clock", lambda x: app.ir_a_agenda(), "Mi Agenda PRO"]]

        ScrollView:
            MDBoxLayout:
                id: main_container
                orientation: 'vertical'
                padding: "16dp"
                spacing: "15dp"
                adaptive_height: True

                MDCard:
                    id: card_datos_generales
                    orientation: 'vertical'
                    padding: "16dp"
                    spacing: "12dp"
                    radius: [12,]
                    elevation: 2
                    md_bg_color: 0.14, 0.14, 0.14, 1
                    adaptive_height: True

                    MDTextField:
                        id: field_nombre_emisor
                        hint_text: "Tu Nombre / Empresa (Emisor)"
                        hint_text_color_normal: 0.6, 0.6, 0.6, 1
                        text_color_normal: 1, 1, 1, 1
                        line_color_normal: 0.3, 0.3, 0.3, 1
                        line_color_focus: 0.89, 0.11, 0.13, 1

                    MDTextField:
                        id: field_telefono_emisor
                        hint_text: "Tu Teléfono / WhatsApp"
                        hint_text_color_normal: 0.6, 0.6, 0.6, 1
                        text_color_normal: 1, 1, 1, 1
                        line_color_normal: 0.3, 0.3, 0.3, 1
                        line_color_focus: 0.89, 0.11, 0.13, 1

                    MDTextField:
                        id: field_proyecto
                        hint_text: "Nombre del Proyecto *"
                        hint_text_color_normal: 0.6, 0.6, 0.6, 1
                        text_color_normal: 1, 1, 1, 1
                        line_color_normal: 0.3, 0.3, 0.3, 1
                        line_color_focus: 0.89, 0.11, 0.13, 1

                    MDTextField:
                        id: field_servicio
                        hint_text: "Servicio a Realizar (Detalle)"
                        hint_text_color_normal: 0.6, 0.6, 0.6, 1
                        text_color_normal: 1, 1, 1, 1
                        line_color_normal: 0.3, 0.3, 0.3, 1
                        line_color_focus: 0.89, 0.11, 0.13, 1
                        multiline: True

                MDCard:
                    orientation: 'vertical'
                    padding: "16dp"
                    spacing: "12dp"
                    radius: [12,]
                    elevation: 2
                    md_bg_color: 0.14, 0.14, 0.14, 1
                    adaptive_height: True

                    MDLabel:
                        id: lbl_opcion_a
                        text: "Opción A: Materiales Globales (Solo Valor)"
                        font_style: "Caption"
                        theme_text_color: "Custom"
                        text_color: 0.7, 0.7, 0.7, 1

                    MDTextField:
                        id: field_materiales_global
                        hint_text: "Monto Total Materiales ($)"
                        hint_text_color_normal: 0.6, 0.6, 0.6, 1
                        text_color_normal: 1, 1, 1, 1
                        line_color_normal: 0.3, 0.3, 0.3, 1
                        line_color_focus: 0.89, 0.11, 0.13, 1
                        input_filter: "int"

                    MDLabel:
                        id: lbl_opcion_b
                        text: "O bien, Opción B: Detallar Materiales Ítem por Ítem"
                        font_style: "Caption"
                        theme_text_color: "Custom"
                        text_color: 0.7, 0.7, 0.7, 1

                    MDBoxLayout:
                        id: box_desglose_lista
                        orientation: 'vertical'
                        spacing: "10dp"
                        adaptive_height: True

                    MDRaisedButton:
                        id: btn_add_material
                        text: "+ Agregar Ítem Detallado"
                        icon: "plus"
                        md_bg_color: 0.2, 0.2, 0.2, 1
                        text_color: 1, 1, 1, 1
                        pos_hint: {"center_x": .5}
                        size_hint_x: 1
                        elevation: 1
                        on_release: app.agregar_linea_material()

                MDCard:
                    orientation: 'vertical'
                    padding: "16dp"
                    spacing: "12dp"
                    radius: [12,]
                    elevation: 2
                    md_bg_color: 0.14, 0.14, 0.14, 1
                    adaptive_height: True

                    MDTextField:
                        id: field_mano_obra
                        hint_text: "Mano de Obra ($)"
                        hint_text_color_normal: 0.6, 0.6, 0.6, 1
                        text_color_normal: 1, 1, 1, 1
                        line_color_normal: 0.3, 0.3, 0.3, 1
                        line_color_focus: 0.89, 0.11, 0.13, 1
                        input_filter: "int"

                    MDTextField:
                        id: field_mano_obra_detalle
                        hint_text: "Detalle Mano de Obra (Opcional)"
                        hint_text_color_normal: 0.6, 0.6, 0.6, 1
                        text_color_normal: 1, 1, 1, 1
                        line_color_normal: 0.3, 0.3, 0.3, 1
                        line_color_focus: 0.89, 0.11, 0.13, 1
                        multiline: True

                    MDLabel:
                        id: lbl_garantia_titulo
                        text: "Garantía del Servicio:"
                        font_style: "Caption"
                        theme_text_color: "Custom"
                        text_color: 0.7, 0.7, 0.7, 1

                    Spinner:
                        id: spin_garantia
                        text: "6 Meses"
                        values: ["30 Días", "3 Meses", "6 Meses", "1 Año", "Sin Garantía"]
                        background_color: 0.2, 0.2, 0.2, 1
                        color: 1, 1, 1, 1
                        size_hint_y: None
                        height: "45dp"

                    MDTextField:
                        id: field_garantia_custom
                        hint_text: "O escribe garantía personalizada (opcional)..."
                        hint_text_color_normal: 0.6, 0.6, 0.6, 1
                        text_color_normal: 1, 1, 1, 1
                        line_color_normal: 0.3, 0.3, 0.3, 1
                        line_color_focus: 0.89, 0.11, 0.13, 1

                MDCard:
                    orientation: 'vertical'
                    padding: "16dp"
                    spacing: "12dp"
                    radius: [12,]
                    elevation: 2
                    md_bg_color: 0.14, 0.14, 0.14, 1
                    adaptive_height: True

                    MDRaisedButton:
                        id: btn_plazo_titulo
                        text: "Plazo de Ejecución (Para el PDF)"
                        icon: "calendar-range"
                        md_bg_color: 0.2, 0.2, 0.2, 1
                        text_color: 1, 1, 1, 1
                        pos_hint: {"center_x": .5}
                        size_hint_x: 1
                        elevation: 0

                    MDLabel:
                        id: lbl_f_ini_titulo
                        text: "Fecha de Inicio:"
                        font_style: "Caption"
                        theme_text_color: "Custom"
                        text_color: 0.7, 0.7, 0.7, 1

                    MDBoxLayout:
                        spacing: "8dp"
                        size_hint_y: None
                        height: "45dp"

                        Spinner:
                            id: spin_dia_ini
                            text: "Día"
                            values: [str(i) for i in range(1, 32)]
                            background_color: 0.2, 0.2, 0.2, 1
                            color: 1, 1, 1, 1
                            size_hint_x: 0.25

                        Spinner:
                            id: spin_mes_ini
                            text: "Mes"
                            values: ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
                            background_color: 0.2, 0.2, 0.2, 1
                            color: 1, 1, 1, 1
                            size_hint_x: 0.5

                        Spinner:
                            id: spin_ano_ini
                            text: "2026"
                            values: app.anos_lista
                            background_color: 0.2, 0.2, 0.2, 1
                            color: 1, 1, 1, 1
                            size_hint_x: 0.25

                    MDLabel:
                        id: lbl_f_fin_titulo
                        text: "Fecha de Término (Opcional):"
                        font_style: "Caption"
                        theme_text_color: "Custom"
                        text_color: 0.7, 0.7, 0.7, 1

                    MDBoxLayout:
                        spacing: "8dp"
                        size_hint_y: None
                        height: "45dp"

                        Spinner:
                            id: spin_dia_fin
                            text: "Día"
                            values: ["Día"] + [str(i) for i in range(1, 32)]
                            background_color: 0.2, 0.2, 0.2, 1
                            color: 1, 1, 1, 1
                            size_hint_x: 0.25

                        Spinner:
                            id: spin_mes_fin
                            text: "Mes"
                            values: ["Mes", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
                            background_color: 0.2, 0.2, 0.2, 1
                            color: 1, 1, 1, 1
                            size_hint_x: 0.5

                        Spinner:
                            id: spin_ano_fin
                            text: "2026"
                            values: app.anos_lista
                            background_color: 0.2, 0.2, 0.2, 1
                            color: 1, 1, 1, 1
                            size_hint_x: 0.25

                MDBoxLayout:
                    spacing: "10dp"
                    adaptive_height: True
                    size_hint_y: None
                    height: "50dp"

                    MDRaisedButton:
                        id: btn_generar_pdf
                        text: "GENERAR PDF"
                        icon: "file-pdf-box"
                        font_size: "14sp"
                        bold: True
                        md_bg_color: 0.89, 0.11, 0.13, 1
                        text_color: 1, 1, 1, 1
                        size_hint_x: 0.5
                        elevation: 3
                        on_release: app.generar_solo_pdf_action()

                    MDRaisedButton:
                        id: btn_guardar_agenda
                        text: "GUARDAR EN AGENDA PRO"
                        icon: "calendar-plus"
                        font_size: "13sp"
                        bold: True
                        md_bg_color: 0.2, 0.2, 0.2, 1
                        text_color: 1, 1, 1, 1
                        size_hint_x: 0.5
                        elevation: 3
                        on_release: app.guardar_en_agenda_action()

<AgendaScreen>:
    name: "agenda"
    md_bg_color: 0.08, 0.08, 0.08, 1

    MDBoxLayout:
        orientation: 'vertical'

        MDTopAppBar:
            id: top_bar_agenda
            title: "Mi Agenda PRO (Panel de Control)"
            elevation: 0
            md_bg_color: 0.12, 0.12, 0.12, 1
            specific_text_color: 0.9, 0.9, 0.9, 1
            left_action_items: [["arrow-left", lambda x: app.ir_a_cotizador(), "Volver"]]

        MDBoxLayout:
            size_hint_y: None
            height: "50dp"
            padding: "4dp"
            spacing: "4dp"
            md_bg_color: 0.14, 0.14, 0.14, 1

            MDRaisedButton:
                id: tab_btn_obras
                text: "Obras"
                font_size: "11sp"
                md_bg_color: 0.89, 0.11, 0.13, 1
                text_color: 1, 1, 1, 1
                size_hint_x: 0.33
                on_release: app.cambiar_pestana_agenda("obras")

            MDRaisedButton:
                id: tab_btn_bitacoras
                text: "Bitácoras"
                font_size: "11sp"
                md_bg_color: 0.2, 0.2, 0.2, 1
                text_color: 1, 1, 1, 1
                size_hint_x: 0.33
                on_release: app.cambiar_pestana_agenda("bitacoras")

            MDRaisedButton:
                id: tab_btn_notas
                text: "Notas"
                font_size: "11sp"
                md_bg_color: 0.2, 0.2, 0.2, 1
                text_color: 1, 1, 1, 1
                size_hint_x: 0.33
                on_release: app.cambiar_pestana_agenda("notas")

        MDBoxLayout:
            id: contenedor_pestanas_agenda
            orientation: 'vertical'
            padding: "16dp"
            spacing: "12dp"

<PerfilScreen>:
    name: "perfil"
    md_bg_color: 0.08, 0.08, 0.08, 1

    MDBoxLayout:
        orientation: 'vertical'

        MDTopAppBar:
            id: top_bar_perfil
            title: "Perfil Profesional / Empresa"
            elevation: 0
            md_bg_color: 0.12, 0.12, 0.12, 1
            specific_text_color: 0.9, 0.9, 0.9, 1
            left_action_items: [["arrow-left", lambda x: app.ir_a_cotizador(), "Volver"]]
            right_action_items: [["share-variant", lambda x: app.compartir_perfil_action(), "Compartir Perfil"]]

        ScrollView:
            MDBoxLayout:
                orientation: 'vertical'
                padding: "20dp"
                spacing: "15dp"
                size_hint_x: 0.95
                pos_hint: {"center_x": .5}
                adaptive_height: True

                MDCard:
                    orientation: 'vertical'
                    padding: "16dp"
                    spacing: "12dp"
                    radius: [12,]
                    elevation: 2
                    md_bg_color: 0.14, 0.14, 0.14, 1
                    adaptive_height: True

                    MDLabel:
                        text: "Datos para Encabezado de Cotización"
                        font_style: "Subtitle1"
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        halign: "center"

                    MDTextField:
                        id: field_perfil_nombre
                        hint_text: "Nombre / Empresa (Ej: Maestranza JP)"
                        hint_text_color_normal: 0.6, 0.6, 0.6, 1
                        text_color_normal: 1, 1, 1, 1
                        line_color_normal: 0.3, 0.3, 0.3, 1
                        line_color_focus: 0.89, 0.11, 0.13, 1

                    MDTextField:
                        id: field_perfil_telefono
                        hint_text: "Teléfono Principal / WhatsApp"
                        hint_text_color_normal: 0.6, 0.6, 0.6, 1
                        text_color_normal: 1, 1, 1, 1
                        line_color_normal: 0.3, 0.3, 0.3, 1
                        line_color_focus: 0.89, 0.11, 0.13, 1

                    MDTextField:
                        id: field_perfil_correo
                        hint_text: "Correo Electrónico"
                        hint_text_color_normal: 0.6, 0.6, 0.6, 1
                        text_color_normal: 1, 1, 1, 1
                        line_color_normal: 0.3, 0.3, 0.3, 1
                        line_color_focus: 0.89, 0.11, 0.13, 1

                    MDTextField:
                        id: field_perfil_extra
                        hint_text: "Contacto / Red Adicional (Libre)"
                        hint_text_color_normal: 0.6, 0.6, 0.6, 1
                        text_color_normal: 1, 1, 1, 1
                        line_color_normal: 0.3, 0.3, 0.3, 1
                        line_color_focus: 0.89, 0.11, 0.13, 1

                    MDBoxLayout:
                        spacing: "10dp"
                        size_hint_y: None
                        height: "45dp"

                        MDRaisedButton:
                            id: btn_guardar_perfil
                            text: "Guardar Perfil"
                            bold: True
                            md_bg_color: 0.89, 0.11, 0.13, 1
                            text_color: 1, 1, 1, 1
                            size_hint_x: 0.5
                            on_release: app.guardar_perfil_action()

                        MDRaisedButton:
                            id: btn_borrar_perfil
                            text: "Borrar Perfil"
                            bold: True
                            md_bg_color: 0.25, 0.25, 0.25, 1
                            text_color: 1, 1, 1, 1
                            size_hint_x: 0.5
                            on_release: app.borrar_perfil_action()

                MDCard:
                    orientation: 'vertical'
                    padding: "16dp"
                    spacing: "12dp"
                    radius: [12,]
                    elevation: 2
                    md_bg_color: 0.14, 0.14, 0.14, 1
                    adaptive_height: True

                    MDRaisedButton:
                        id: btn_politica_privacidad
                        text: "Política de Privacidad"
                        bold: True
                        md_bg_color: 0.2, 0.2, 0.2, 1
                        text_color: 1, 1, 1, 1
                        size_hint_x: 1
                        on_release: app.mostrar_politica_privacidad()

                MDCard:
                    orientation: 'vertical'
                    padding: "16dp"
                    spacing: "12dp"
                    radius: [12,]
                    elevation: 2
                    md_bg_color: 0.14, 0.14, 0.14, 1
                    adaptive_height: True

                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: "40dp"
                        
                        MDLabel:
                            id: lbl_qr_titulo
                            text: "Tarjeta de Contacto QR"
                            font_style: "Subtitle1"
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 1
                            halign: "left"
                            valign: "center"

                        MDIconButton:
                            icon: "share-variant"
                            theme_text_color: "Custom"
                            text_color: 0.89, 0.11, 0.13, 1
                            on_release: app.compartir_perfil_action()
                            pos_hint: {"center_y": .5}

                    MDLabel:
                        id: lbl_qr_sub
                        text: "Escanea para agregar contacto automáticamente:"
                        font_style: "Caption"
                        theme_text_color: "Custom"
                        text_color: 0.7, 0.7, 0.7, 1
                        halign: "center"

                    AnchorLayout:
                        anchor_x: "center"
                        anchor_y: "center"
                        size_hint_y: None
                        height: "220dp"

                        MDCard:
                            size_hint: None, None
                            size: "200dp", "200dp"
                            padding: "8dp"
                            radius: [12,]
                            elevation: 0
                            md_bg_color: 1, 1, 1, 1

                            AnchorLayout:
                                anchor_x: "center"
                                anchor_y: "center"

                                AsyncImage:
                                    id: qr_image_widget
                                    source: ""
                                    size_hint: None, None
                                    size: "184dp", "184dp"
"""


class CotizadorScreen(Screen):
    pass


class AgendaScreen(Screen):
    pass


class PerfilScreen(Screen):
    pass


class CotizadorApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.lista_idiomas_display = [
            ("Español", "ES"),
            ("English", "EN")
        ]
        self.idioma_index = 0
        self.materiales_inputs = []
        
        self.es_usuario_pro = True  
        self.agenda_trabajos = []
        self.lista_notas_generales = []
        self.perfil_datos = {"nombre": "", "telefono": "", "correo": "", "extra": ""}
        
        self.indice_obra_editando = None
        self.filtro_actual = "Pendiente"
        self.pestana_agenda_actual = "obras"
        self.anos_lista = ANOS_DISPONIBLES
        
        self.cargar_datos_locales()


    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Red"
        return Builder.load_string(KV)


    def on_start(self):
        self.actualizar_textos_ui()
        self.verificar_visibilidad_campos_individuales()
        self.actualizar_qr_widget()
        if not self.materiales_inputs:
            self.agregar_linea_material()


    def obtener_ruta_archivo_datos(self):
        return os.path.join(obtener_ruta_descargas(), "cotizador_pro_datos.json")


    def guardar_datos_locales(self):
        try:
            datos = {
                "es_usuario_pro": self.es_usuario_pro,
                "agenda_trabajos": self.agenda_trabajos,
                "lista_notas_generales": self.lista_notas_generales,
                "perfil_datos": self.perfil_datos
            }
            path = self.obtener_ruta_archivo_datos()
            with open(path, "w", encoding="utf-8") as f:
                json.dump(datos, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print("Error al guardar datos:", e)


    def cargar_datos_locales(self):
        try:
            path = self.obtener_ruta_archivo_datos()
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    datos = json.load(f)
                    self.es_usuario_pro = True
                    self.agenda_trabajos = datos.get("agenda_trabajos", [])
                    self.lista_notas_generales = datos.get("lista_notas_generales", [])
                    self.perfil_datos = datos.get("perfil_datos", {"nombre": "", "telefono": "", "correo": "", "extra": ""})
        except Exception as e:
            print("Error al cargar datos:", e)


    def actualizar_qr_widget(self):
        scr_p = self.root.get_screen('perfil')
        p_nom = self.perfil_datos.get("nombre", "").strip()
        p_tel = self.perfil_datos.get("telefono", "").strip()
        p_corr = self.perfil_datos.get("correo", "").strip()
        p_ext = self.perfil_datos.get("extra", "").strip()

        nombre_qr = p_nom if p_nom else "Servicio Profesional"
        tel_qr = p_tel if p_tel else ""
        email_qr = p_corr if p_corr else ""
        web_qr = p_ext if p_ext else ""

        texto_mecard = f"MECARD:N:{nombre_qr};TEL:{tel_qr};EMAIL:{email_qr};NOTE:{web_qr};;"
        
        url_codificada = urllib.parse.quote(texto_mecard)
        api_qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={url_codificada}"
        
        scr_p.ids.qr_image_widget.source = api_qr_url
        scr_p.ids.qr_image_widget.reload()


    def mostrar_politica_privacidad(self):
        _, idioma_code = self.lista_idiomas_display[self.idioma_index]
        t_lang = TEXTOS[idioma_code]
        self.mostrar_alerta(t_lang['privacy_title'], t_lang['privacy_desc'])


    def compartir_perfil_action(self):
        p_nom = self.perfil_datos.get("nombre", "").strip()
        p_tel = self.perfil_datos.get("telefono", "").strip()
        p_corr = self.perfil_datos.get("correo", "").strip()
        p_ext = self.perfil_datos.get("extra", "").strip()

        texto_crudo = (
            "¡Hola! 👋 Te comparto mis datos de contacto y servicios profesionales:\n"
            f"📌 *{p_nom}*\n"
            f"📞 Teléfono / WhatsApp: {p_tel}\n"
            f"✉️ Correo: {p_corr}\n"
            f"🔗 {p_ext}\n"
            "¡Contáctanos para tus proyectos y cotizaciones! 💼"
        )
        
        try:
            if platform == 'android':
                intent = Intent()
                intent.setAction(Intent.ACTION_SEND)
                
                utf8_bytes = texto_crudo.encode('utf-8')
                java_string = StringClass(utf8_bytes, 'UTF-8')
                
                intent.putExtra(Intent.EXTRA_TEXT, java_string)
                intent.setType('text/plain')
                currentActivity = PythonActivity.mActivity
                chooser = Intent.createChooser(intent, StringClass("Compartir Tarjeta PRO"))
                currentActivity.startActivity(chooser)
            else:
                url_whatsapp = f"https://api.whatsapp.com/send?text={urllib.parse.quote(texto_crudo)}"
                webbrowser.open(url_whatsapp)
        except Exception as e:
            self.mostrar_alerta("Aviso", "No se pudo invocar el menú de compartir nativo.")


    def verificar_visibilidad_campos_individuales(self):
        scr = self.root.get_screen('cotizador')
        card_datos = scr.ids.card_datos_generales
        
        tiene_nombre_perfil = bool(self.perfil_datos.get("nombre", "").strip())
        if tiene_nombre_perfil:
            scr.ids.field_nombre_emisor.opacity = 0
            scr.ids.field_nombre_emisor.height = 0
            scr.ids.field_nombre_emisor.disabled = True
        else:
            scr.ids.field_nombre_emisor.opacity = 1
            scr.ids.field_nombre_emisor.height = "48dp"
            scr.ids.field_nombre_emisor.disabled = False

        tiene_tel_perfil = bool(self.perfil_datos.get("telefono", "").strip())
        if tiene_tel_perfil:
            scr.ids.field_telefono_emisor.opacity = 0
            scr.ids.field_telefono_emisor.height = 0
            scr.ids.field_telefono_emisor.disabled = True
        else:
            scr.ids.field_telefono_emisor.opacity = 1
            scr.ids.field_telefono_emisor.height = "48dp"
            scr.ids.field_telefono_emisor.disabled = False

        if tiene_nombre_perfil and tiene_tel_perfil:
            card_datos.padding = "10dp"
            card_datos.spacing = "6dp"
        else:
            card_datos.padding = "16dp"
            card_datos.spacing = "12dp"


    def ir_a_agenda(self):
        self.root.transition = SlideTransition(direction='left')
        self.root.current = "agenda"
        self.actualizar_vista_agenda()


    def ir_a_perfil(self):
        _, idioma_code = self.lista_idiomas_display[self.idioma_index]
        if not self.es_usuario_pro:
            msg = "Esta función requiere la versión Pro (membresía activa)." if idioma_code == "ES" else "This feature requires the Pro version."
            self.mostrar_alerta("Acceso Restringido", msg)
            return
        
        scr_p = self.root.get_screen('perfil')
        scr_p.ids.field_perfil_nombre.text = self.perfil_datos.get("nombre", "")
        scr_p.ids.field_perfil_telefono.text = self.perfil_datos.get("telefono", "")
        scr_p.ids.field_perfil_correo.text = self.perfil_datos.get("correo", "")
        scr_p.ids.field_perfil_extra.text = self.perfil_datos.get("extra", "")

        self.actualizar_qr_widget()
        self.root.transition = SlideTransition(direction='left')
        self.root.current = "perfil"


    def guardar_perfil_action(self):
        scr_p = self.root.get_screen('perfil')
        self.perfil_datos = {
            "nombre": scr_p.ids.field_perfil_nombre.text.strip(),
            "telefono": scr_p.ids.field_perfil_telefono.text.strip(),
            "correo": scr_p.ids.field_perfil_correo.text.strip(),
            "extra": scr_p.ids.field_perfil_extra.text.strip()
        }
        self.guardar_datos_locales()
        self.verificar_visibilidad_campos_individuales()
        self.actualizar_qr_widget()
        _, idioma_code = self.lista_idiomas_display[self.idioma_index]
        msg = "Perfil profesional guardado correctamente." if idioma_code == "ES" else "Professional profile saved successfully."
        self.mostrar_alerta("Perfil Guardado", msg)


    def borrar_perfil_action(self):
        scr_p = self.root.get_screen('perfil')
        scr_p.ids.field_perfil_nombre.text = ""
        scr_p.ids.field_perfil_telefono.text = ""
        scr_p.ids.field_perfil_correo.text = ""
        scr_p.ids.field_perfil_extra.text = ""
        self.perfil_datos = {"nombre": "", "telefono": "", "correo": "", "extra": ""}
        self.guardar_datos_locales()
        self.verificar_visibilidad_campos_individuales()
        self.actualizar_qr_widget()
        _, idioma_code = self.lista_idiomas_display[self.idioma_index]
        msg = "Perfil profesional borrado." if idioma_code == "ES" else "Professional profile deleted."
        self.mostrar_alerta("Perfil Borrado", msg)


    def ir_a_cotizador(self):
        self.indice_obra_editando = None
        self.actualizar_texto_boton_guardar()
        self.root.transition = SlideTransition(direction='right')
        self.root.current = "cotizador"


    def actualizar_texto_boton_guardar(self):
        scr = self.root.get_screen('cotizador')
        _, idioma_code = self.lista_idiomas_display[self.idioma_index]
        t_lang = TEXTOS[idioma_code]
        if self.indice_obra_editando is not None:
            scr.ids.btn_guardar_agenda.text = t_lang['btn_actualizar']
        else:
            scr.ids.btn_guardar_agenda.text = t_lang['btn_agenda']


    def cambiar_idioma_siguiente(self):
        self.idioma_index = (self.idioma_index + 1) % len(self.lista_idiomas_display)
        nombre_display, idioma_code = self.lista_idiomas_display[self.idioma_index]
        self.actualizar_textos_ui()
        msg = f"Idioma cambiado a: {nombre_display}" if idioma_code == "ES" else f"Language switched to: {nombre_display}"
        title_msg = "Idioma Actualizado" if idioma_code == "ES" else "Language Updated"
        self.mostrar_alerta(title_msg, msg)


    def actualizar_textos_ui(self):
        _, idioma_code = self.lista_idiomas_display[self.idioma_index]
        t_lang = TEXTOS[idioma_code]
        scr = self.root.get_screen('cotizador')
        scr_agenda = self.root.get_screen('agenda')
        scr_perfil = self.root.get_screen('perfil')

        # Pantalla Principal
        scr.ids.top_bar.title = t_lang['app_title']
        scr.ids.field_nombre_emisor.hint_text = t_lang['nombre_emisor_hint']
        scr.ids.field_telefono_emisor.hint_text = t_lang['tel_emisor_hint']
        scr.ids.field_proyecto.hint_text = t_lang['pro_hint']
        scr.ids.field_servicio.hint_text = t_lang['ser_hint']

        # Actualización de etiquetas estáticas
        scr.ids.lbl_opcion_a.text = t_lang['opcion_a_lbl']
        scr.ids.lbl_opcion_b.text = t_lang['opcion_b_lbl']

        scr.ids.field_materiales_global.hint_text = t_lang['mat_hint']
        scr.ids.btn_add_material.text = t_lang['btn_add_mat']
        scr.ids.field_mano_obra.hint_text = t_lang['mo_hint']
        scr.ids.field_mano_obra_detalle.hint_text = t_lang['mo_det_hint']
        
        scr.ids.lbl_garantia_titulo.text = t_lang['garantia_lbl']
        scr.ids.btn_plazo_titulo.text = t_lang['btn_plazo']
        scr.ids.lbl_f_ini_titulo.text = t_lang['lbl_f_ini']
        scr.ids.lbl_f_fin_titulo.text = t_lang['lbl_f_fin']
        
        scr.ids.btn_generar_pdf.text = t_lang['btn_pdf']
        self.actualizar_texto_boton_guardar()

        # Agenda PRO
        scr_agenda.ids.top_bar_agenda.title = t_lang['agenda_title']

        # Perfil Profesional
        scr_perfil.ids.top_bar_perfil.title = t_lang['perfil_title']
        scr_perfil.ids.field_perfil_nombre.hint_text = "Nombre / Empresa (Ej: Maestranza JP)" if idioma_code == "ES" else "Name / Company (Ex: Metalworks JP)"
        scr_perfil.ids.field_perfil_telefono.hint_text = "Teléfono Principal / WhatsApp" if idioma_code == "ES" else "Main Phone / WhatsApp"
        scr_perfil.ids.field_perfil_correo.hint_text = "Correo Electrónico" if idioma_code == "ES" else "Email"
        scr_perfil.ids.field_perfil_extra.hint_text = "Contacto / Red Adicional (Libre)" if idioma_code == "ES" else "Additional Contact / Social"
        scr_perfil.ids.btn_guardar_perfil.text = "Guardar Perfil" if idioma_code == "ES" else "Save Profile"
        scr_perfil.ids.btn_borrar_perfil.text = "Borrar Perfil" if idioma_code == "ES" else "Delete Profile"
        scr_perfil.ids.btn_politica_privacidad.text = "Política de Privacidad" if idioma_code == "ES" else "Privacy Policy"
        scr_perfil.ids.lbl_qr_titulo.text = "Tarjeta de Contacto QR" if idioma_code == "ES" else "QR Contact Card"
        scr_perfil.ids.lbl_qr_sub.text = "Escanea para agregar contacto automáticamente:" if idioma_code == "ES" else "Scan to add contact automatically:"

        # Actualizar contenido si la agenda está abierta
        if self.root.current == "agenda":
            self.actualizar_vista_agenda()


    def agregar_linea_material(self, cant=1, nombre="", precio=""):
        box_contenedor = self.root.get_screen('cotizador').ids.box_desglose_lista
        linea = MDBoxLayout(spacing="5dp", adaptive_height=True)
        
        _, idioma_code = self.lista_idiomas_display[self.idioma_index]
        hint_cant = "Cant." if idioma_code == "ES" else "Qty"
        hint_nom = "Ítem" if idioma_code == "ES" else "Item"
        hint_pre = "Costo ($)" if idioma_code == "ES" else "Cost ($)"


        t_cant = MDTextField(hint_text=hint_cant, input_filter="int", size_hint_x=0.20, text=str(cant))
        t_nombre = MDTextField(hint_text=hint_nom, size_hint_x=0.45, text=str(nombre))
        t_precio = MDTextField(hint_text=hint_pre, input_filter="int", size_hint_x=0.25, text=str(precio) if precio else "")
        
        btn_eliminar = MDIconButton(
            icon="trash-can-outline",
            theme_text_color="Custom",
            text_color=(0.89, 0.11, 0.13, 1),
            pos_hint={'center_y': .5}
        )
        
        item_data = (t_cant, t_nombre, t_precio, linea)
        btn_eliminar.on_release = lambda: self.eliminar_linea_material(item_data)


        linea.add_widget(t_cant)
        linea.add_widget(t_nombre)
        linea.add_widget(t_precio)
        linea.add_widget(btn_eliminar)
        
        self.materiales_inputs.append(item_data)
        box_contenedor.add_widget(linea)


    def eliminar_linea_material(self, item_data):
        box_contenedor = self.root.get_screen('cotizador').ids.box_desglose_lista
        linea_widget = item_data[3]
        if linea_widget in box_contenedor.children:
            box_contenedor.remove_widget(linea_widget)
        if item_data in self.materiales_inputs:
            self.materiales_inputs.remove(item_data)


    def cambiar_pestana_agenda(self, pestana):
        self.pestana_agenda_actual = pestana
        btn_obras = self.root.get_screen('agenda').ids.tab_btn_obras
        btn_bitacoras = self.root.get_screen('agenda').ids.tab_btn_bitacoras
        btn_notas = self.root.get_screen('agenda').ids.tab_btn_notas


        btn_obras.md_bg_color = (0.2, 0.2, 0.2, 1)
        btn_bitacoras.md_bg_color = (0.2, 0.2, 0.2, 1)
        btn_notas.md_bg_color = (0.2, 0.2, 0.2, 1)


        if pestana == "obras":
            btn_obras.md_bg_color = (0.89, 0.11, 0.13, 1)
        elif pestana == "bitacoras":
            btn_bitacoras.md_bg_color = (0.89, 0.11, 0.13, 1)
        else:
            btn_notas.md_bg_color = (0.89, 0.11, 0.13, 1)


        self.actualizar_vista_agenda()


    def filtrar_agenda(self, estado):
        self.filtro_actual = estado
        self.actualizar_vista_agenda()


    def actualizar_vista_agenda(self):
        scr_agenda = self.root.get_screen('agenda')
        _, idioma_code = self.lista_idiomas_display[self.idioma_index]
        t_lang = TEXTOS[idioma_code]

        scr_agenda.ids.tab_btn_obras.text = t_lang['tab_obras']
        scr_agenda.ids.tab_btn_bitacoras.text = t_lang['tab_bitacoras']
        scr_agenda.ids.tab_btn_notas.text = t_lang['tab_notas']

        contenedor = scr_agenda.ids.contenedor_pestanas_agenda
        contenedor.clear_widgets()


        if self.pestana_agenda_actual == "obras":
            filtro_box = MDBoxLayout(size_hint_y=None, height="45dp", spacing="6dp")
            
            labels_filtros = [
                ("Todos", t_lang['filtro_todos'], (0.25, 0.25, 0.25, 1)),
                ("Pendiente", t_lang['filtro_pendiente'], (0.85, 0.55, 0.1, 1)),
                ("En Ejecución", t_lang['filtro_en_ejecucion'], (0.12, 0.65, 0.25, 1)),
                ("Finalizado", t_lang['filtro_finalizado'], (0.15, 0.4, 0.85, 1))
            ]
            
            for clave_estado, txt_mostrar, color_val in labels_filtros:
                btn_f = MDRaisedButton(text=txt_mostrar, font_size="11sp", md_bg_color=color_val, text_color=(1, 1, 1, 1))
                btn_f.bind(on_release=lambda x, e=clave_estado: self.filtrar_agenda(e))
                filtro_box.add_widget(btn_f)
            
            contenedor.add_widget(filtro_box)


            scroll = ScrollView()
            lista_box = MDBoxLayout(orientation='vertical', spacing="12dp", adaptive_height=True)


            trabajos_filtrados = [
                (idx, t) for idx, t in enumerate(self.agenda_trabajos)
                if self.filtro_actual == "Todos" or t.get('estado', 'Pendiente') == self.filtro_actual
            ]


            if not trabajos_filtrados:
                msg_vacio = t_lang['msg_no_proyectos']
                card = MDCard(orientation='vertical', padding="16dp", radius=[12], size_hint_y=None, height="80dp", md_bg_color=(0.14, 0.14, 0.14, 1))
                card.add_widget(MDLabel(text=msg_vacio, halign="center", theme_text_color="Custom", text_color=(0.7, 0.7, 0.7, 1)))
                lista_box.add_widget(card)
            else:
                for idx, trabajo in trabajos_filtrados:
                    card = MDCard(orientation='vertical', padding="12dp", spacing="8dp", radius=[12], size_hint_y=None, height="165dp", md_bg_color=(0.14, 0.14, 0.14, 1), elevation=2)
                    
                    top_row = MDBoxLayout(orientation='horizontal', size_hint_y=None, height="30dp")
                    lbl_tit = MDLabel(text=f"[b]{trabajo.get('proyecto', 'Sin nombre')}[/b]", markup=True, font_style="Subtitle1", theme_text_color="Custom", text_color=(1, 1, 1, 1), size_hint_x=0.55)
                    
                    estado_actual = trabajo.get('estado', 'Pendiente')
                    
                    if estado_actual == "Pendiente":
                        color_bg_spinner = (0.85, 0.55, 0.1, 1)
                    elif estado_actual == "En Ejecución":
                        color_bg_spinner = (0.12, 0.65, 0.25, 1)
                    else:
                        color_bg_spinner = (0.15, 0.4, 0.85, 1)

                    spinner_estado = Spinner(
                        text=estado_actual,
                        values=("Pendiente", "En Ejecución", "Finalizado"),
                        size_hint=(None, None),
                        size=("130dp", "30dp"),
                        background_color=color_bg_spinner,
                        color=(1, 1, 1, 1),
                        pos_hint={'right': 1}
                    )
                    spinner_estado.bind(text=lambda spinner, val, i=idx: self.cambiar_estado_directo(i, val))
                    
                    top_row.add_widget(lbl_tit)
                    top_row.add_widget(spinner_estado)

                    lbl_det = MDLabel(text=f"{t_lang['lbl_fecha_card']} {trabajo.get('inicio', 'Por coordinar')} | [{estado_actual.upper()}]", font_style="Caption", theme_text_color="Custom", text_color=(0.7, 0.7, 0.7, 1), size_hint_y=None, height="20dp")

                    acciones_box = MDBoxLayout(orientation='horizontal', spacing="6dp", size_hint_y=None, height="40dp")
                    
                    btn_editar = MDRaisedButton(text=t_lang['card_edit'], font_size="10sp", bold=True, md_bg_color=(0.25, 0.25, 0.25, 1), text_color=(1,1,1,1), size_hint_x=0.25)
                    btn_editar.bind(on_release=lambda x, i=idx: self.cargar_obra_para_editar(i))

                    btn_duplicar = MDRaisedButton(text=t_lang['card_copy'], font_size="10sp", bold=True, md_bg_color=(0.15, 0.35, 0.5, 1), text_color=(1,1,1,1), size_hint_x=0.25)
                    btn_duplicar.bind(on_release=lambda x, i=idx: self.duplicar_obra(i))

                    btn_pdf = MDRaisedButton(text="PDF", font_size="10sp", bold=True, md_bg_color=(0.1, 0.5, 0.3, 1), text_color=(1,1,1,1), size_hint_x=0.2)
                    btn_pdf.bind(on_release=lambda x, i=idx: self.generar_pdf_desde_agenda(i))

                    btn_eliminar = MDRaisedButton(text=t_lang['card_del'], font_size="10sp", bold=True, md_bg_color=(0.6, 0.1, 0.1, 1), text_color=(1,1,1,1), size_hint_x=0.3)
                    btn_eliminar.bind(on_release=lambda x, i=idx: self.eliminar_obra(i))

                    acciones_box.add_widget(btn_editar)
                    acciones_box.add_widget(btn_duplicar)
                    acciones_box.add_widget(btn_pdf)
                    acciones_box.add_widget(btn_eliminar)

                    card.add_widget(top_row)
                    card.add_widget(lbl_det)
                    card.add_widget(acciones_box)
                    lista_box.add_widget(card)

            scroll.add_widget(lista_box)
            contenedor.add_widget(scroll)

        elif self.pestana_agenda_actual == "bitacoras":
            scroll_b = ScrollView()
            box_b = MDBoxLayout(orientation='vertical', spacing="14dp", adaptive_height=True)

            if not self.agenda_trabajos:
                msg_vacio_b = "No hay proyectos guardados para ver bitácoras." if idioma_code == "ES" else "No saved projects found for logs."
                card = MDCard(orientation='vertical', padding="16dp", radius=[12], size_hint_y=None, height="80dp", md_bg_color=(0.14, 0.14, 0.14, 1))
                card.add_widget(MDLabel(text=msg_vacio_b, halign="center", theme_text_color="Custom", text_color=(0.7, 0.7, 0.7, 1)))
                box_b.add_widget(card)
            else:
                for idx, trabajo in enumerate(self.agenda_trabajos):
                    card = MDCard(orientation='vertical', padding="14dp", spacing="10dp", radius=[12], size_hint_y=None, height="265dp", md_bg_color=(0.14, 0.14, 0.14, 1), elevation=2)
                    lbl_tit = MDLabel(text=f"[b]Project: {trabajo.get('proyecto', 'Sin nombre')}[/b]", markup=True, font_style="Subtitle1", theme_text_color="Custom", text_color=(1, 1, 1, 1))
                    
                    bitacora_lista = trabajo.get('bitacora', [])
                    historial_txt = "\n".join(bitacora_lista) if bitacora_lista else ("Sin notas registradas." if idioma_code=="ES" else "No recorded notes.")
                    
                    lbl_hist = MDLabel(
                        text=f"History:\n{historial_txt}",
                        font_style="Body2",
                        theme_text_color="Custom",
                        text_color=(0.8, 0.8, 0.8, 1),
                        size_hint_y=None,
                        height="85dp"
                    )

                    txt_nota_rapida = MDTextField(hint_text="Escribe una nueva nota..." if idioma_code=="ES" else "Write a new note...", size_hint_y=None, height="40dp", text_color_normal=(1,1,1,1))
                    
                    btns_box = MDBoxLayout(spacing="6dp", size_hint_y=None, height="35dp")
                    
                    btn_guardar_n = MDRaisedButton(text="Guardar" if idioma_code=="ES" else "Save", font_size="10sp", bold=True, md_bg_color=(0.89, 0.11, 0.13, 1), text_color=(1,1,1,1), size_hint_x=0.4)
                    btn_guardar_n.bind(on_release=lambda x, i=idx, tf=txt_nota_rapida: self.agregar_nota_desde_pestana(i, tf.text))

                    btn_borrar_ultima = MDRaisedButton(text="Borrar Última" if idioma_code=="ES" else "Delete Last", font_size="10sp", bold=True, md_bg_color=(0.3, 0.3, 0.3, 1), text_color=(1,1,1,1), size_hint_x=0.3)
                    btn_borrar_ultima.bind(on_release=lambda x, i=idx: self.borrarultima_nota(i))

                    btn_limpiar = MDRaisedButton(text="Limpiar Todo" if idioma_code=="ES" else "Clear All", font_size="10sp", bold=True, md_bg_color=(0.5, 0.1, 0.1, 1), text_color=(1,1,1,1), size_hint_x=0.3)
                    btn_limpiar.bind(on_release=lambda x, i=idx: self.limpiar_bitacora(i))

                    btns_box.add_widget(btn_guardar_n)
                    btns_box.add_widget(btn_borrar_ultima)
                    btns_box.add_widget(btn_limpiar)

                    card.add_widget(lbl_tit)
                    card.add_widget(lbl_hist)
                    card.add_widget(txt_nota_rapida)
                    card.add_widget(btns_box)
                    box_b.add_widget(card)

            scroll_b.add_widget(box_b)
            contenedor.add_widget(scroll_b)

        else:
            scroll_n = ScrollView()
            box_n = MDBoxLayout(orientation='vertical', spacing="14dp", adaptive_height=True)

            card_nueva = MDCard(orientation='vertical', padding="14dp", spacing="10dp", radius=[12], size_hint_y=None, height="210dp", md_bg_color=(0.14, 0.14, 0.14, 1), elevation=2)
            lbl_crear_tit = MDLabel(text="[b]Crear Nueva Nota[/b]" if idioma_code=="ES" else "[b]Create New Note[/b]", markup=True, font_style="Subtitle1", theme_text_color="Custom", text_color=(1, 1, 1, 1))
            
            txt_nuevo_titulo = MDTextField(hint_text="Título" if idioma_code=="ES" else "Title", size_hint_y=None, height="45dp", text_color_normal=(1,1,1,1))
            txt_nuevo_contenido = MDTextField(hint_text="Empiece a escribir..." if idioma_code=="ES" else "Start typing...", multiline=True, size_hint_y=None, height="55dp", text_color_normal=(1,1,1,1))
            
            btn_guardar_nueva = MDRaisedButton(text="Guardar Nota" if idioma_code=="ES" else "Save Note", font_size="12sp", bold=True, md_bg_color=(0.89, 0.11, 0.13, 1), text_color=(1,1,1,1), size_hint_x=1)
            btn_guardar_nueva.bind(on_release=lambda x, tt=txt_nuevo_titulo, tc=txt_nuevo_contenido: self.agregar_nota_general_action(tt, tc))

            card_nueva.add_widget(lbl_crear_tit)
            card_nueva.add_widget(txt_nuevo_titulo)
            card_nueva.add_widget(txt_nuevo_contenido)
            card_nueva.add_widget(btn_guardar_nueva)
            box_n.add_widget(card_nueva)

            if not self.lista_notas_generales:
                card_vacia = MDCard(orientation='vertical', padding="16dp", radius=[12], size_hint_y=None, height="70dp", md_bg_color=(0.14, 0.14, 0.14, 1))
                card_vacia.add_widget(MDLabel(text="No hay notas guardadas." if idioma_code=="ES" else "No saved notes.", halign="center", theme_text_color="Custom", text_color=(0.7, 0.7, 0.7, 1)))
                box_n.add_widget(card_vacia)
            else:
                for idx, nota_obj in enumerate(self.lista_notas_generales):
                    card_nota = MDCard(orientation='vertical', padding="14dp", spacing="8dp", radius=[12], size_hint_y=None, height="215dp", md_bg_color=(0.14, 0.14, 0.14, 1), elevation=2)
                    
                    lbl_fecha = MDLabel(text=f"[b]Nota #{idx+1}[/b] - {nota_obj.get('fecha', '')}", markup=True, font_style="Caption", size_hint_y=None, height="20dp", theme_text_color="Custom", text_color=(0.7, 0.7, 0.7, 1))
                    txt_editar_titulo = MDTextField(text=nota_obj.get('titulo', ''), hint_text="Título", size_hint_y=None, height="42dp", text_color_normal=(1,1,1,1))
                    txt_editar_contenido = MDTextField(text=nota_obj.get('texto', ''), hint_text="Empiece a escribir...", multiline=True, size_hint_y=None, height="65dp", text_color_normal=(1,1,1,1))
                    
                    btns_nota_box = MDBoxLayout(spacing="8dp", size_hint_y=None, height="35dp")
                    
                    btn_act = MDRaisedButton(text="Actualizar" if idioma_code=="ES" else "Update", font_size="10sp", bold=True, md_bg_color=(0.1, 0.5, 0.2, 1), text_color=(1,1,1,1), size_hint_x=0.5)
                    btn_act.bind(on_release=lambda x, i=idx, tt=txt_editar_titulo, tc=txt_editar_contenido: self.actualizar_nota_general(i, tt.text, tc.text))

                    btn_del = MDRaisedButton(text="Borrar" if idioma_code=="ES" else "Delete", font_size="10sp", bold=True, md_bg_color=(0.6, 0.1, 0.1, 1), text_color=(1,1,1,1), size_hint_x=0.5)
                    btn_del.bind(on_release=lambda x, i=idx: self.borrar_nota_general(i))

                    btns_nota_box.add_widget(btn_act)
                    btns_nota_box.add_widget(btn_del)

                    card_nota.add_widget(lbl_fecha)
                    card_nota.add_widget(txt_editar_titulo)
                    card_nota.add_widget(txt_editar_contenido)
                    card_nota.add_widget(btns_nota_box)
                    box_n.add_widget(card_nota)

            scroll_n.add_widget(box_n)
            contenedor.add_widget(scroll_n)


    def cambiar_estado_directo(self, index, nuevo_estado):
        if not nuevo_estado or self.agenda_trabajos[index].get('estado') == nuevo_estado:
            return
        self.agenda_trabajos[index]['estado'] = nuevo_estado
        self.guardar_datos_locales()
        self.actualizar_vista_agenda()


    def cargar_obra_para_editar(self, index):
        if 0 <= index < len(self.agenda_trabajos):
            t = self.agenda_trabajos[index]
            self.indice_obra_editando = index
            
            scr = self.root.get_screen('cotizador')
            scr.ids.field_nombre_emisor.text = str(t.get('nombre_emisor', ''))
            scr.ids.field_telefono_emisor.text = str(t.get('telefono_emisor', ''))
            scr.ids.field_proyecto.text = str(t.get('proyecto', ''))
            scr.ids.field_servicio.text = str(t.get('servicio', ''))
            scr.ids.field_materiales_global.text = str(t.get('mat_costo', ''))
            scr.ids.field_mano_obra.text = str(t.get('mo_costo', ''))
            scr.ids.field_mano_obra_detalle.text = str(t.get('mo_det', ''))
            scr.ids.spin_garantia.text = str(t.get('garantia', '6 Meses'))
            
            box_contenedor = scr.ids.box_desglose_lista
            box_contenedor.clear_widgets()
            self.materiales_inputs = []
            
            mat_lista = t.get('mat_lista', [])
            if mat_lista:
                for item in mat_lista:
                    if isinstance(item, (list, tuple)) and len(item) >= 3:
                        self.agregar_linea_material(item[0], item[1], item[2])
                    else:
                        self.agregar_linea_material(1, str(item), "")
            else:
                self.agregar_linea_material()
                
            self.actualizar_texto_boton_guardar()
            self.root.transition = SlideTransition(direction='right')
            self.root.current = "cotizador"


    def duplicar_obra(self, index):
        if 0 <= index < len(self.agenda_trabajos):
            t = self.agenda_trabajos[index]
            self.indice_obra_editando = None
            
            scr = self.root.get_screen('cotizador')
            scr.ids.field_nombre_emisor.text = str(t.get('nombre_emisor', ''))
            scr.ids.field_telefono_emisor.text = str(t.get('telefono_emisor', ''))
            scr.ids.field_proyecto.text = str(t.get('proyecto', '')) + " (Copia)"
            scr.ids.field_servicio.text = str(t.get('servicio', ''))
            scr.ids.field_materiales_global.text = str(t.get('mat_costo', ''))
            scr.ids.field_mano_obra.text = str(t.get('mo_costo', ''))
            scr.ids.field_mano_obra_detalle.text = str(t.get('mo_det', ''))
            scr.ids.spin_garantia.text = str(t.get('garantia', '6 Meses'))
            
            box_contenedor = scr.ids.box_desglose_lista
            box_contenedor.clear_widgets()
            self.materiales_inputs = []
            
            mat_lista = t.get('mat_lista', [])
            if mat_lista:
                for item in mat_lista:
                    if isinstance(item, (list, tuple)) and len(item) >= 3:
                        self.agregar_linea_material(item[0], item[1], item[2])
                    else:
                        self.agregar_linea_material(1, str(item), "")
            else:
                self.agregar_linea_material()
                
            self.actualizar_texto_boton_guardar()
            self.root.transition = SlideTransition(direction='right')
            self.root.current = "cotizador"


    def generar_pdf_desde_agenda(self, index):
        if 0 <= index < len(self.agenda_trabajos):
            t = self.agenda_trabajos[index]
            _, idioma_code = self.lista_idiomas_display[self.idioma_index]
            proyecto_nombre = str(t.get('proyecto', 'Cotizacion'))
            nombre_limpio = "".join([c for c in proyecto_nombre if c.isalnum() or c in (' ', '_')]).rstrip()
            filename = f"Cotizacion_{nombre_limpio.replace(' ', '_')}.pdf"
            
            try:
                crear_pdf_completo(
                    filename, 
                    str(t.get('nombre_emisor', '')), 
                    str(t.get('telefono_emisor', '')), 
                    proyecto_nombre, 
                    str(t.get('servicio', '')), 
                    str(t.get('mat_costo', '')), 
                    str(t.get('mo_costo', '')), 
                    str(t.get('mo_det', '')), 
                    str(t.get('garantia', '')), 
                    bool(t.get('usar_detallado', False)), 
                    t.get('mat_lista', []), 
                    str(t.get('idioma', idioma_code)), 
                    str(t.get('inicio', '')), 
                    str(t.get('fin', '')), 
                    self.perfil_datos
                )
                msg = f"PDF generado en Descargas:\n\n{filename}" if idioma_code == "ES" else f"PDF created in Downloads:\n\n{filename}"
                self.mostrar_alerta("PDF Rápido", msg)
            except Exception as e:
                self.mostrar_alerta("Error", f"No se pudo generar el PDF: {str(e)}")


    def eliminar_obra(self, index):
        if 0 <= index < len(self.agenda_trabajos):
            proyecto_nombre = self.agenda_trabajos[index].get('proyecto', 'Proyecto')
            self.agenda_trabajos.pop(index)
            self.guardar_datos_locales()
            self.actualizar_vista_agenda()
            _, idioma_code = self.lista_idiomas_display[self.idioma_index]
            msg = f"Se eliminó el proyecto '{proyecto_nombre}' y su bitácora asociada." if idioma_code == "ES" else f"Project '{proyecto_nombre}' and its associated log were deleted."
            self.mostrar_alerta("Obra Eliminada", msg)


    def agregar_nota_general_action(self, tf_titulo, tf_contenido):
        titulo = tf_titulo.text.strip()
        contenido = tf_contenido.text.strip()
        _, idioma_code = self.lista_idiomas_display[self.idioma_index]
        
        if titulo or contenido:
            timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
            self.lista_notas_generales.append({
                "fecha": timestamp, 
                "titulo": titulo if titulo else ("Sin título" if idioma_code=="ES" else "Untitled"), 
                "texto": contenido
            })
            self.guardar_datos_locales()
            tf_titulo.text = ""
            tf_contenido.text = ""
            self.actualizar_vista_agenda()
            msg = "Nota agregada correctamente." if idioma_code == "ES" else "Note added successfully."
            title_msg = "Nota Guardada" if idioma_code == "ES" else "Note Saved"
            self.mostrar_alerta(title_msg, msg)
        else:
            msg = "Debes ingresar al menos un título o contenido para la nota." if idioma_code == "ES" else "You must enter at least a title or content for the note."
            title_msg = "Aviso" if idioma_code == "ES" else "Notice"
            self.mostrar_alerta(title_msg, msg)


    def actualizar_nota_general(self, index, nuevo_titulo, nuevo_contenido):
        _, idioma_code = self.lista_idiomas_display[self.idioma_index]
        if nuevo_titulo.strip() or nuevo_contenido.strip():
            self.lista_notas_generales[index]['titulo'] = nuevo_titulo.strip()
            self.lista_notas_generales[index]['texto'] = nuevo_contenido.strip()
            self.guardar_datos_locales()
            self.actualizar_vista_agenda()
            msg = "Nota actualizada correctamente." if idioma_code == "ES" else "Note updated successfully."
            title_msg = "Actualizado" if idioma_code == "ES" else "Updated"
            self.mostrar_alerta(title_msg, msg)
        else:
            msg = "La nota no puede quedar completamente vacía." if idioma_code == "ES" else "Note cannot be completely empty."
            title_msg = "Aviso" if idioma_code == "ES" else "Notice"
            self.mostrar_alerta(title_msg, msg)


    def borrar_nota_general(self, index):
        _, idioma_code = self.lista_idiomas_display[self.idioma_index]
        if 0 <= index < len(self.lista_notas_generales):
            self.lista_notas_generales.pop(index)
            self.guardar_datos_locales()
            self.actualizar_vista_agenda()
            msg = "Nota eliminada correctamente." if idioma_code == "ES" else "Note deleted successfully."
            title_msg = "Nota Eliminada" if idioma_code == "ES" else "Note Deleted"
            self.mostrar_alerta(title_msg, msg)


    def agregar_nota_desde_pestana(self, index, texto_nota):
        if texto_nota.strip():
            timestamp = datetime.datetime.now().strftime("%d/%m %H:%M")
            self.agenda_trabajos[index]['bitacora'].append(f"[{timestamp}] {texto_nota.strip()}")
            self.guardar_datos_locales()
            self.actualizar_vista_agenda()
            _, idioma_code = self.lista_idiomas_display[self.idioma_index]
            msg = "Se agregó la nota correctamente." if idioma_code == "ES" else "Note added successfully."
            title_msg = "Bitácora Actualizada" if idioma_code == "ES" else "Log Updated"
            self.mostrar_alerta(title_msg, msg)


    def borrarultima_nota(self, index):
        t = self.agenda_trabajos[index]
        _, idioma_code = self.lista_idiomas_display[self.idioma_index]
        if len(t['bitacora']) > 1:
            t['bitacora'].pop()
            self.guardar_datos_locales()
            self.actualizar_vista_agenda()
            msg = "Se ha eliminado la última entrada de la bitácora." if idioma_code == "ES" else "The last log entry has been removed."
            title_msg = "Nota Eliminada" if idioma_code == "ES" else "Note Deleted"
            self.mostrar_alerta(title_msg, msg)
        else:
            msg = "No se puede eliminar la nota inicial de creación del proyecto." if idioma_code == "ES" else "Cannot delete the initial project creation note."
            title_msg = "Aviso" if idioma_code == "ES" else "Notice"
            self.mostrar_alerta(title_msg, msg)


    def limpiar_bitacora(self, index):
        t = self.agenda_trabajos[index]
        _, idioma_code = self.lista_idiomas_display[self.idioma_index]
        if len(t['bitacora']) > 0:
            t['bitacora'] = [t['bitacora'][0]]
            self.guardar_datos_locales()
            self.actualizar_vista_agenda()
            msg = "Se han borrado las notas adicionales, conservando el registro inicial." if idioma_code == "ES" else "Additional notes cleared, keeping the initial entry."
            title_msg = "Bitácora Limpiada" if idioma_code == "ES" else "Log Cleared"
            self.mostrar_alerta(title_msg, msg)


    def extraer_datos_formulario(self):
        scr = self.root.get_screen('cotizador')
        nombre_emisor = scr.ids.field_nombre_emisor.text
        tel_emisor = scr.ids.field_telefono_emisor.text
        pro = scr.ids.field_proyecto.text
        ser = scr.ids.field_servicio.text
        mat_glob = scr.ids.field_materiales_global.text
        mo = scr.ids.field_mano_obra.text
        mo_det = scr.ids.field_mano_obra_detalle.text
        
        gar_spinner = scr.ids.spin_garantia.text
        gar_custom = scr.ids.field_garantia_custom.text.strip()
        gar = gar_custom if gar_custom else gar_spinner


        _, idioma_code = self.lista_idiomas_display[self.idioma_index]


        if not pro.strip():
            msg = "Por favor ingresa al menos el Nombre del Proyecto." if idioma_code == "ES" else "Please enter at least the Project Name."
            title_msg = "Campo Requerido" if idioma_code == "ES" else "Required Field"
            self.mostrar_alerta(title_msg, msg)
            return None


        lista_mat_limpia = []
        total_mat_detallado = 0
        
        for field_cant, field_nom, field_pre, _ in self.materiales_inputs:
            cant_raw = field_cant.text.strip()
            nom = field_nom.text.strip()
            pre_raw = field_pre.text.strip()
            
            if pre_raw:
                try:
                    cant_val = int(cant_raw) if cant_raw else 1
                    if cant_val <= 0: cant_val = 1
                except ValueError:
                    cant_val = 1
                
                try:
                    val = int(pre_raw)
                    nombre_final = nom if nom else ("Material sin nombre" if idioma_code=="ES" else "Unnamed material")
                    lista_mat_limpia.append((cant_val, nombre_final, val))
                    total_mat_detallado += (cant_val * val)
                except ValueError:
                    pass


        usar_detallado = len(lista_mat_limpia) > 0
        
        try:
            mat_glob_val = int(mat_glob) if mat_glob and mat_glob.strip() else 0
        except ValueError:
            mat_glob_val = 0


        total_mat_calculado = total_mat_detallado if usar_detallado else mat_glob_val


        try:
            total_mo_calculado = int(mo) if mo and mo.strip() else 0
        except ValueError:
            total_mo_calculado = 0


        if (total_mat_calculado + total_mo_calculado) <= 0:
            msg = "Debes ingresar al menos un costo en Materiales o Mano de Obra." if idioma_code == "ES" else "You must enter at least a cost for Materials or Labor."
            title_msg = "Monto Requerido" if idioma_code == "ES" else "Amount Required"
            self.mostrar_alerta(title_msg, msg)
            return None


        d_ini = scr.ids.spin_dia_ini.text
        m_ini = scr.ids.spin_mes_ini.text
        a_ini = scr.ids.spin_ano_ini.text
        f_inicio_str = f"{d_ini} de {m_ini} del {a_ini}" if d_ini not in ["Dia", "Día"] and m_ini != "Mes" else ""


        d_fin = scr.ids.spin_dia_fin.text
        m_fin = scr.ids.spin_mes_fin.text
        a_fin = scr.ids.spin_ano_fin.text
        f_termino_str = f"{d_fin} de {m_fin} del {a_fin}" if d_fin not in ["Dia", "Día"] and m_fin != "Mes" else ""


        return {
            "nombre_emisor": nombre_emisor, "telefono_emisor": tel_emisor, "proyecto": pro, "servicio": ser,
            "mat_costo": mat_glob, "mo_costo": mo, "mo_det": mo_det, "garantia": gar,
            "usar_detallado": usar_detallado, "mat_lista": lista_mat_limpia, "idioma": idioma_code,
            "f_ini": f_inicio_str, "f_fin": f_termino_str
        }


    def generar_solo_pdf_action(self):
        datos = self.extraer_datos_formulario()
        if not datos:
            return
        
        _, idioma_code = self.lista_idiomas_display[self.idioma_index]
        nombre_limpio = "".join([c for c in datos['proyecto'] if c.isalnum() or c in (' ', '_')]).rstrip()
        filename = f"Cotizacion_{nombre_limpio.replace(' ', '_')}.pdf"
        
        try:
            path = crear_pdf_completo(
                filename, datos['nombre_emisor'], datos['telefono_emisor'], datos['proyecto'], datos['servicio'], 
                datos['mat_costo'], datos['mo_costo'], datos['mo_det'], 
                datos['garantia'], datos['usar_detallado'], datos['mat_lista'], datos['idioma'], 
                datos['f_ini'], datos['f_fin'], self.perfil_datos
            )


            msg = f"El PDF se creó en Descargas:\n\n{filename}\n\n(Versión PRO: PDFs Ilimitados)" if idioma_code == "ES" else f"PDF created in Downloads:\n\n{filename}"
            title_msg = "Cotización Generada" if idioma_code == "ES" else "Quotation Generated"
            self.mostrar_alerta(title_msg, msg)
        except Exception as e:
            self.mostrar_alerta("Error", f"Ocurrió un problema: {str(e)}")


    def guardar_en_agenda_action(self):
        datos = self.extraer_datos_formulario()
        if not datos:
            return


        timestamp = datetime.datetime.now().strftime("%d/%m %H:%M")
        _, idioma_code = self.lista_idiomas_display[self.idioma_index]

        if self.indice_obra_editando is not None:
            idx = self.indice_obra_editando
            estado_actual = self.agenda_trabajos[idx].get('estado', 'Pendiente')
            bitacora_actual = self.agenda_trabajos[idx].get('bitacora', [])
            bitacora_actual.append(f"[{timestamp}] Proyecto actualizado desde el menú principal")

            self.agenda_trabajos[idx] = {
                "proyecto": datos['proyecto'],
                "nombre_emisor": datos['nombre_emisor'],
                "telefono_emisor": datos['telefono_emisor'],
                "inicio": datos['f_ini'] if datos['f_ini'] else "Por coordinar",
                "fin": datos['f_fin'],
                "servicio": datos['servicio'],
                "mat_costo": datos['mat_costo'],
                "mo_costo": datos['mo_costo'],
                "mo_det": datos['mo_det'],
                "garantia": datos['garantia'],
                "usar_detallado": datos['usar_detallado'],
                "mat_lista": datos['mat_lista'],
                "idioma": datos['idioma'],
                "estado": estado_actual,
                "bitacora": bitacora_actual
            }
            self.indice_obra_editando = None
            self.actualizar_texto_boton_guardar()
            self.guardar_datos_locales()
            
            msg = f"El proyecto '{datos['proyecto']}' se ha actualizado correctamente." if idioma_code == "ES" else f"Project '{datos['proyecto']}' updated successfully."
            self.mostrar_alerta("Obra Actualizada", msg)
            self.ir_a_agenda()
        else:
            trabajo_info = {
                "proyecto": datos['proyecto'],
                "nombre_emisor": datos['nombre_emisor'],
                "telefono_emisor": datos['telefono_emisor'],
                "inicio": datos['f_ini'] if datos['f_ini'] else "Por coordinar",
                "fin": datos['f_fin'],
                "servicio": datos['servicio'],
                "mat_costo": datos['mat_costo'],
                "mo_costo": datos['mo_costo'],
                "mo_det": datos['mo_det'],
                "garantia": datos['garantia'],
                "usar_detallado": datos['usar_detallado'],
                "mat_lista": datos['mat_lista'],
                "idioma": datos['idioma'],
                "estado": "Pendiente",
                "bitacora": [f"[{timestamp}] Proyecto guardado en Agenda PRO"]
            }
            self.agenda_trabajos.append(trabajo_info)
            self.guardar_datos_locales()
            
            msg = f"El proyecto '{datos['proyecto']}' se agregó correctamente a la agenda." if idioma_code == "ES" else f"Project '{datos['proyecto']}' added to agenda."
            title_msg = "Guardado en Agenda PRO" if idioma_code == "ES" else "Saved to Agenda PRO"
            self.mostrar_alerta(title_msg, msg)


    def mostrar_alerta(self, titulo, texto):
        self.dialog = MDDialog(
            title=titulo,
            text=texto,
            buttons=[MDFlatButton(text="Aceptar", on_release=lambda x: self.dialog.dismiss())]
        )
        self.dialog.open()


if __name__ == "__main__":
    CotizadorApp().run()
