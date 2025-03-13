class Formatters:
    """Formateadores para mostrar datos en Telegram."""
    
    @staticmethod
    def format_currency(amount):
        """
        Formatea un valor monetario para mostrar en Telegram.
        
        Args:
            amount (float): Monto a formatear
            
        Returns:
            str: Monto formateado como string (ej: $100.50)
        """
        return f"${amount:.2f}"
    
    @staticmethod
    def format_date(date_str):
        """
        Formatea una fecha para mostrar en Telegram.
        
        Args:
            date_str (str): Fecha en formato ISO (ej: 2025-03-10T18:30:01.115)
            
        Returns:
            str: Fecha formateada (ej: 10/03/2025)
        """
        if not date_str:
            return "Fecha desconocida"
        
        try:
            # Extraer la parte de la fecha (antes de la T)
            date_part = date_str.split("T")[0]
            # Separar año, mes y día
            year, month, day = date_part.split("-")
            # Formatear como día/mes/año
            return f"{day}/{month}/{year}"
        except Exception:
            return date_str
    
    @staticmethod
    def format_members(members):
        """Formatea la lista de miembros para mostrar en Telegram."""
        return "\n".join([f"- ID: {m['id']}, Nombre: {m['name']}, Teléfono: {m.get('phone', 'No disponible')}" for m in members])
    
    @staticmethod
    def format_family_info(family):
        """
        Formatea la información de una familia para mostrar en Telegram.
        
        Args:
            family (dict): Diccionario con la información de la familia
            
        Returns:
            str: Texto formateado con la información de la familia
        """
        try:
            # Verificar que family sea un diccionario
            if not isinstance(family, dict):
                print(f"Error: family no es un diccionario, es {type(family)}")
                return "Error al formatear la información de la familia."
            
            # Obtener datos básicos de la familia
            family_id = family.get('id', 'Desconocido')
            name = family.get('name', 'Sin nombre')
            created_at = family.get('created_at', '')
            
            # Formatear la fecha de creación
            date_str = created_at.split("T")[0] if created_at else "Fecha desconocida"
            
            # Obtener la lista de miembros
            members = family.get('members', [])
            members_count = len(members)
            
            # Formatear la lista de miembros
            members_list = []
            for member in members:
                member_id = member.get('id', 'Desconocido')
                member_name = member.get('name', 'Sin nombre')
                member_phone = member.get('phone', 'No disponible')
                members_list.append(f"• *{member_name}* (ID: `{member_id}`)")
            
            members_text = "\n".join(members_list) if members_list else "No hay miembros registrados."
            
            # Construir el mensaje completo
            from ui.messages import Messages
            return Messages.FAMILY_INFO.format(
                name=name,
                id=family_id,
                members_count=members_count,
                members_list=members_text
            )
            
        except Exception as e:
            print(f"Error al formatear información de familia: {e}")
            import traceback
            traceback.print_exc()
            return "Error al formatear la información de la familia."
    
    @staticmethod
    def format_expenses(expenses, member_names=None):
        """Formatea la lista de gastos para mostrar en Telegram.
        
        Args:
            expenses: Lista de gastos
            member_names: Diccionario de ID -> nombre para mostrar nombres en lugar de IDs
            
        Returns:
            str: Texto formateado con los gastos
        """
        print(f"Formateando gastos: {expenses}")
        
        if not expenses:
            return "No hay gastos registrados."
        
        # Si no se proporciona el diccionario de nombres, crear uno vacío
        if member_names is None:
            member_names = {}
        
        print(f"Nombres de miembros disponibles: {member_names}")
        
        result = []
        for expense in expenses:
            try:
                print(f"Procesando gasto: {expense}")
                
                # Formatear la fecha
                created_at = expense.get("created_at", "")
                date_str = Formatters.format_date(created_at) if hasattr(Formatters, 'format_date') else (created_at.split("T")[0] if created_at else "Fecha desconocida")
                
                # Obtener el nombre de quien pagó
                paid_by_id = expense.get("paid_by", "")
                print(f"Gasto pagado por ID={paid_by_id} ({type(paid_by_id)})")
                
                # Buscar el nombre del miembro de varias maneras
                paid_by_name = None
                
                # 1. Buscar como string (el caso más común y seguro)
                if paid_by_id is not None:
                    str_id = str(paid_by_id)
                    if str_id in member_names:
                        paid_by_name = member_names[str_id]
                        print(f"Nombre encontrado usando string ID: {paid_by_name}")
                
                # 2. Buscar como número si es aplicable
                if not paid_by_name and paid_by_id is not None:
                    if isinstance(paid_by_id, int) or (isinstance(paid_by_id, str) and paid_by_id.isdigit()):
                        numeric_id = int(paid_by_id) if isinstance(paid_by_id, str) else paid_by_id
                        if numeric_id in member_names:
                            paid_by_name = member_names[numeric_id]
                            print(f"Nombre encontrado usando numeric ID: {paid_by_name}")
                
                # 3. Valor por defecto si no se encuentra
                if not paid_by_name:
                    paid_by_name = f"Usuario {paid_by_id}"
                    print(f"No se encontró nombre, usando valor por defecto: {paid_by_name}")
                
                # Formatear la lista de miembros entre los que se divide
                split_among = expense.get("split_among", [])
                if split_among and isinstance(split_among, list):
                    # Verificar si cada elemento es un diccionario (formato API) o un ID (formato antiguo)
                    if split_among and isinstance(split_among[0], dict):
                        # Formato API: cada elemento es un diccionario con información del miembro
                        split_names = [member.get("name", f"Usuario {member.get('id', 'Desconocido')}") for member in split_among]
                    else:
                        # Formato antiguo: cada elemento es un ID
                        split_names = []
                        for member_id in split_among:
                            # Buscar el nombre del miembro de varias maneras
                            name = None
                            
                            # 1. Buscar como string
                            if member_id is not None:
                                str_id = str(member_id)
                                if str_id in member_names:
                                    name = member_names[str_id]
                            
                            # 2. Buscar como número
                            if not name and member_id is not None:
                                if isinstance(member_id, int) or (isinstance(member_id, str) and member_id.isdigit()):
                                    numeric_id = int(member_id) if isinstance(member_id, str) else member_id
                                    if numeric_id in member_names:
                                        name = member_names[numeric_id]
                            
                            # 3. Valor por defecto
                            if not name:
                                name = f"Usuario {member_id}"
                                
                            split_names.append(name)
                    
                    split_text = ", ".join(split_names)
                else:
                    split_text = "Todos los miembros"
                
                # Crear el texto del gasto
                expense_text = (
                    f"🧾 *{expense.get('description', 'Sin descripción')}*\n"
                    f"💰 Monto: *${expense.get('amount', 0):.2f}*\n"
                    f"👤 Pagado por: *{paid_by_name}*\n"
                    f"👥 Dividido entre: *{split_text}*\n"
                    f"📅 Fecha: *{date_str}*\n"
                    f"🆔 ID: `{expense.get('id', 'Desconocido')}`"
                )
                result.append(expense_text)
            except Exception as e:
                print(f"Error al formatear gasto: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        if not result:
            return "No se pudieron formatear los gastos."
            
        return "\n\n" + "\n\n".join(result)
    
    @staticmethod
    def format_balances(balances, member_names=None, current_member_id=None):
        """Formatea los balances para mostrar en Telegram según el esquema de la API.
        
        La API devuelve los balances en formato de lista de balances por miembro
        con deudas y créditos detallados.
        
        Args:
            balances: Lista de balances de miembros
            member_names: Diccionario de ID -> nombre (opcional, ya que los nombres 
                          vienen incluidos en la respuesta de la API)
            current_member_id: ID del miembro actual que realiza la consulta (para mostrarlo primero)
        """
        print(f"Formateando balances")
        
        # Si no hay balances, mostrar un mensaje
        if not balances:
            return "No hay balances disponibles."
        
        # Si no se proporciona el diccionario de nombres, crear uno vacío
        if member_names is None:
            member_names = {}
        
        # Determinar el formato de los balances por la presencia de campos específicos
        if isinstance(balances, list) and len(balances) > 0 and isinstance(balances[0], dict):
            if "member_id" in balances[0] and "debts" in balances[0] and "credits" in balances[0]:
                return Formatters._format_member_balances(balances, member_names, current_member_id)
        
        # Si no se puede determinar el formato, mostrar mensaje de error
        print(f"Formato de balances no reconocido")
        return "Formato de balances no reconocido. Por favor contacte al administrador."
    
    @staticmethod
    def _format_member_balances(balances, member_names, current_member_id=None):
        """Formatea los balances por miembro, mostrando primero al usuario actual."""
        result = []
        current_member_balance = None
        other_members_balances = []
        
        print(f"Formateando balances de miembros, current_member_id={current_member_id}")
        
        for balance in balances:
            try:
                # Verificar que balance sea un diccionario
                if not isinstance(balance, dict):
                    print(f"Error: balance no es un diccionario, es {type(balance)}")
                    continue
                
                # Obtener el ID y nombre del miembro
                member_id = balance.get('member_id')
                member_name = balance.get('name', 'Desconocido')
                
                # Formatear deudas (lo que debe a otros)
                debts = balance.get('debts', [])
                if debts and len(debts) > 0 and isinstance(debts, list):
                    debts_list = []
                    for d in debts:
                        # Usar preferentemente el campo to_id para la lógica interna
                        to_id = d.get('to_id')
                        # Obtener el nombre del acreedor directamente del campo 'to' (ahora alias de to_name)
                        to_name = d.get('to', 'Desconocido')
                        
                        # Registrar la información para depuración
                        print(f"Deuda: to_id={to_id}, to_name={to_name}")
                        
                        debts_list.append(f"• {to_name}: ${d.get('amount', 0):.2f}")
                    debts_text = "\n".join(debts_list)
                else:
                    debts_text = "• No debe a nadie"
                
                # Formatear créditos (lo que le deben)
                credits = balance.get('credits', [])
                if credits and len(credits) > 0 and isinstance(credits, list):
                    credits_list = []
                    for c in credits:
                        # Usar preferentemente el campo from_id para la lógica interna
                        from_id = c.get('from_id')
                        # Obtener el nombre del deudor directamente del campo 'from' (ahora alias de from_name)
                        from_name = c.get('from', 'Desconocido')
                        
                        # Registrar la información para depuración
                        print(f"Crédito: from_id={from_id}, from_name={from_name}")
                        
                        credits_list.append(f"• {from_name}: ${c.get('amount', 0):.2f}")
                    credits_text = "\n".join(credits_list)
                else:
                    credits_text = "• Nadie le debe"
                
                # Formatear el balance con emojis según si es positivo, negativo o cero
                net_balance = balance.get('net_balance', 0)
                if net_balance > 0:
                    balance_emoji = "🟢"  # Verde para balance positivo
                elif net_balance < 0:
                    balance_emoji = "🔴"  # Rojo para balance negativo
                else:
                    balance_emoji = "⚪"  # Blanco para balance cero
                
                # Verificar si este es el miembro actual para resaltarlo en negrita
                is_current_member = current_member_id is not None and str(member_id) == str(current_member_id)
                
                # Formatear el nombre según si es el miembro actual o no
                # En Telegram Markdown, usamos * para negrita y símbolos adicionales para destacar al usuario actual
                if is_current_member:
                    formatted_name = f"*{member_name}* 👈"  # Negrita con un emoji indicador
                else:
                    formatted_name = f"{member_name}"  # Sin formato especial para otros miembros
                
                # Construir el mensaje completo para este miembro
                member_text = (
                    f"👤 {formatted_name}\n"
                    f"{balance_emoji} Balance neto: *${net_balance:.2f}*\n"
                    f"💰 Total a favor: *${balance.get('total_owed', 0):.2f}*\n"
                    f"💸 Total a deber: *${balance.get('total_debt', 0):.2f}*\n\n"
                    f"*Deudas:*\n{debts_text}\n\n"
                    f"*Créditos:*\n{credits_text}"
                )
                
                # Determinar si este es el miembro actual o no
                if is_current_member:
                    print(f"Este es el miembro actual: {member_id} == {current_member_id}")
                    current_member_balance = member_text
                else:
                    other_members_balances.append(member_text)
                
            except Exception as e:
                print(f"Error al formatear balance: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # Organizar los resultados: primero el miembro actual, luego los demás
        if current_member_balance:
            result.append(current_member_balance)
        
        # Añadir el resto de miembros
        result.extend(other_members_balances)
        
        # Si no hay resultados, mostrar un mensaje
        if not result:
            return "No hay balances disponibles."
            
        return "\n\n".join(result) 