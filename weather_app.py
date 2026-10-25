import flet as ft
import requests

def main(page: ft.Page):
    page.title = "Погода"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 30
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    city_input = ft.TextField(
        label="Введите город",
        hint_text="Например: Moscow",
        width=300,
        on_submit=lambda e: get_weather(e.control.value)
    )

    weather_info = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10
    )
    
    status_text = ft.Text("", color=ft.Colors.RED_400)

    def get_weather(city: str):
        if not city.strip():
            status_text.value = "Пожалуйста, введите название города."
            page.update()
            return
        
        status_text.value = "Загрузка..."
        weather_info.controls.clear()
        page.update()

        try:
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=ru&format=json"
            geo_resp = requests.get(geo_url, timeout=10)
            geo_resp.raise_for_status()
            geo_data = geo_resp.json()
            
            if not geo_data.get("results"):
                status_text.value = "Город не найден. Попробуйте другое название."
                page.update()
                return
            
            location = geo_data["results"][0]
            lat = location["latitude"]
            lon = location["longitude"]
            city_name = location["name"]
            country = location.get("country", "")
            

            weather_url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={lat}&longitude={lon}"
                f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m"
                f"&timezone=auto"
            )
            weather_resp = requests.get(weather_url, timeout=10)
            weather_resp.raise_for_status()
            weather_data = weather_resp.json()
            
            current = weather_data["current"]
            temp = current["temperature_2m"]
            feels_like = current["apparent_temperature"]
            humidity = current["relative_humidity_2m"]
            wind = current["wind_speed_10m"]
            code = current["weather_code"]

            weather_desc = get_weather_description(code)
            
         
            status_text.value = ""
            weather_info.controls = [
                ft.Text(f"{city_name}, {country}", size=28, weight=ft.FontWeight.BOLD),
                ft.Text(weather_desc, size=20, color=ft.Colors.BLUE_GREY_400),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                ft.Text(f"{temp}°C", size=64, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
                ft.Text(f"Ощущается как: {feels_like}°C", size=16),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.WATER_DROP, color=ft.Colors.BLUE_300),
                        ft.Text(f"Влажность: {humidity}%", size=14),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=5,
                ),
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.AIR, color=ft.Colors.BLUE_300),
                        ft.Text(f"Ветер: {wind} км/ч", size=14),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=5,
                ),
            ]
            page.update()
            
        except requests.exceptions.RequestException as e:
            status_text.value = f"Ошибка сети: проверьте подключение к интернету."
            page.update()

    def get_weather_description(code: int) -> str:
        """Перевод кодов WMO в текстовое описание."""
        descriptions = {
            0: "Ясно",
            1: "Преимущественно ясно",
            2: "Переменная облачность",
            3: "Пасмурно",
            45: "Туман",
            48: "Изморозь",
            51: "Легкая морось",
            53: "Умеренная морось",
            55: "Сильная морось",
            61: "Небольшой дождь",
            63: "Умеренный дождь",
            65: "Сильный дождь",
            71: "Небольшой снег",
            73: "Умеренный снег",
            75: "Сильный снег",
            80: "Ливень",
            81: "Сильный ливень",
            82: "Очень сильный ливень",
            95: "Гроза",
        }
        return descriptions.get(code, "Неизвестно")

    page.add(
        ft.Text("Приложение Погоды", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
        city_input,
        status_text,
        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
        weather_info,
    )

import os

if __name__ == "__main__":
    ft.run(
        main,
        view=ft.AppView.WEB_BROWSER,
        port=int(os.environ.get("PORT", 10000)), # Render сам назначит порт
        host="0.0.0.0"
    )
