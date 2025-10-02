def extraer_codigo(c_ban: str) -> str:
    if not c_ban:
        return ""
    
    c_ban = c_ban.strip().upper()

    # Comprobar si empieza por "IMP"
    if not c_ban.startswith("IMP"):
        return ""

    # Quitar el prefijo "IMP"
    resto = c_ban[3:].lstrip(". ").strip()

    # Coger los 3 primeros caracteres del resto
    codigo = resto[:3]

    # Verificar que sean 3 dígitos
    if codigo.isdigit() and len(codigo) == 3:
        return str(int(codigo))  # convierte "001" -> "1", "011" -> "11", "123" -> "123"
    return ""
