import flet as ft
from main import executar_busca

    # Todas as configurações da Interface
def main(page: ft.Page):
    page.title = "Busca e Seleção de Parâmetros"
    page.theme_mode = "black"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"

    # Define o tamanho da Janela
    page.window.width= 400
    page.window.height = 600

    # Impede do usuario redimensione a Janela
    page.window_resizable = False

    # Função e botão para alterar o tema
    def alterar_tema(e):
        page.theme_mode = "dark" if page.theme_mode == "light" else "light"
        page.update()

    botao_tema = ft.ElevatedButton("Mudar Tema", on_click=alterar_tema,
                                   width=100,
                                   height=40
                                   )
    page.floating_action_button = botao_tema   

    # # Título
    # title = ft.Text(
    #     "Parâmetros de Busca",
    #     size=20,
    #     weight="bold",
    #     color="blue600",
    #     text_align=ft.TextAlign.CENTER,
        
    # )

    # Opções de Rede Social
    social_media_label = ft.Text("Rede Social:")
    social_media_dropdown = ft.Dropdown(
        options=[
            ft.dropdown.Option("facebook"),
            ft.dropdown.Option("instagram"),
        ],
        hint_text="Selecione",
        width=200,
    )

    # Opções de Nicho
    niche_label = ft.Text("Nicho:")
    niche_dropdown = ft.Dropdown(
        options=[
            ft.dropdown.Option("roupas"),
            ft.dropdown.Option("pets"),
        ],
        hint_text="Selecione",
        width=200,
    )

    # Opções de E-mail
    email_label = ft.Text("E-mail:")
    email_checkboxes = ft.Row([
        ft.Checkbox(label="Gmail"),
        ft.Checkbox(label="Hotmail"),
    ])

    # Lista de DDDs do Brasil
    ddds_brasil = [
        "11", "12", "13", "14", "15", "16", "17", "18", "19",
        "21", "22", "24", "27", "28",
        "31", "32", "33", "34", "35", "37", "38",
        "41", "42", "43", "44", "45", "46",
        "47", "48", "49",
        "51", "53", "54", "55",
        "61", "62", "64", "65", "66", "67", "68", "69",
        "71", "73", "74", "75", "77",
        "79",
        "81", "82", "83", "84", "85", "86", "87", "88", "89",
        "91", "92", "93", "94", "95", "96", "97", "98", "99"
    ]

    # Opções de Telefone
    phone_label = ft.Text("Telefone (DDD):")
    phone_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option(ddd) for ddd in ddds_brasil],
        hint_text="Selecione",
        width=200,
    )

    # Botão de Confirmar
    def on_confirm_click(e):
        selected_social_media = social_media_dropdown.value
        selected_niche = niche_dropdown.value
        selected_emails = [
            checkbox.label for checkbox in email_checkboxes.controls if checkbox.value]
        selected_phone = phone_dropdown.value

        if not selected_social_media or not selected_niche or not selected_emails or not selected_phone:
            page.snack_bar = ft.SnackBar(
                ft.Text("Por favor, preencha todos os campos."))
            page.snack_bar.open()
            return

        # Monta a query para o back-end
        email_query = " OR ".join(
            [f"@{email.lower()}.com" for email in selected_emails])

        query = (
            f"site:{selected_social_media.lower()}.com \"{selected_niche}\" "
            f"({email_query}) (\"({selected_phone})\" OR \"+55\")"
        )

        # Chama a função do back-end para buscar os dados
        results = executar_busca(
            selected_social_media, selected_niche, email_query, selected_phone)

        if results:
            page.snack_bar = ft.SnackBar(
                ft.Text("Resultados salvos no arquivo 'resultados.csv'."))
        else:
            page.snack_bar = ft.SnackBar(
                ft.Text("Nenhum resultado encontrado."))
        page.snack_bar.open()

    confirm_button = ft.ElevatedButton(
        "Confirmar",
        on_click=on_confirm_click,
        color="white",
        bgcolor="green600",
    )

    # Layout
    page.add(
        ft.Column([
            #title,
            social_media_label, social_media_dropdown,
            niche_label, niche_dropdown,
            email_label, email_checkboxes,
            phone_label, phone_dropdown,
            confirm_button,
        ], spacing=15, alignment="center")
    )


ft.app(target=main)
