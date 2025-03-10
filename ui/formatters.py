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
    def format_balances(balances, member_names=None):
        """Formatea los balances para mostrar en Telegram según el esquema de la API.
        
        La API puede devolver los balances en dos formatos diferentes:
        1. Lista de balances por miembro con deudas y créditos detallados
        2. Lista de transacciones pendientes entre miembros
        
        Args:
            balances: Lista de balances o transacciones
            member_names: Diccionario de ID -> nombre para mostrar nombres en lugar de IDs
        """
        print(f"Formateando balances: {balances}")
        
        # Si no hay balances, mostrar un mensaje
        if not balances:
            return "No hay balances disponibles."
        
        # Si no se proporciona el diccionario de nombres, crear uno vacío
        if member_names is None:
            member_names = {}
            
        print(f"Nombres de miembros disponibles: {member_names}")
        
        # Determinar el formato de los balances
        if isinstance(balances, list) and len(balances) > 0:
            # Verificar si es el formato 1 (balances por miembro)
            if isinstance(balances[0], dict) and "member_id" in balances[0]:
                return Formatters._format_member_balances(balances, member_names)
            # Verificar si es el formato 2 (transacciones pendientes)
            elif isinstance(balances[0], dict) and "from_member" in balances[0] and "to_member" in balances[0]:
                return Formatters._format_pending_transactions(balances, member_names)
        
        # Si no se puede determinar el formato, mostrar los datos en bruto
        print(f"Formato de balances no reconocido: {balances}")
        return f"Datos de balances en formato no reconocido: {balances}"
    
    @staticmethod
    def _format_member_balances(balances, member_names):
        """Formatea los balances por miembro."""
        result = []
        
        print(f"Formateando balances de miembros con nombres: {member_names}")
        
        # Crear un diccionario inverso para buscar nombres por ID numérico
        id_to_name = {}
        for member_id, name in member_names.items():
            # Intentar convertir el ID a entero si es posible
            try:
                if isinstance(member_id, str) and member_id.isdigit():
                    numeric_id = int(member_id)
                    id_to_name[numeric_id] = name
            except (ValueError, TypeError):
                # Si no se puede convertir, mantener el ID original
                pass
        
        print(f"Mapa de ID a nombre: {id_to_name}")
        
        for balance in balances:
            try:
                # Verificar que balance sea un diccionario
                if not isinstance(balance, dict):
                    print(f"Error: balance no es un diccionario, es {type(balance)}")
                    continue
                
                # Obtener el ID del miembro (puede ser string o int)
                member_id = balance.get('member_id', 'Desconocido')
                
                # Intentar obtener el nombre del miembro de varias formas
                member_name = balance.get('name')  # Primero intentar obtenerlo directamente del balance
                
                if not member_name:
                    # Si no está en el balance, intentar obtenerlo del diccionario de nombres
                    member_name = member_names.get(str(member_id))
                
                if not member_name and isinstance(member_id, (int, str)):
                    # Si aún no lo encontramos y el ID es numérico, intentar con el ID numérico
                    try:
                        numeric_id = int(member_id) if isinstance(member_id, str) else member_id
                        member_name = id_to_name.get(numeric_id)
                    except (ValueError, TypeError):
                        pass
                
                # Si aún no tenemos un nombre, usar un valor predeterminado
                if not member_name:
                    member_name = f"Usuario {member_id}"
                
                print(f"Miembro ID: {member_id}, Nombre: {member_name}")
                    
                # Formatear deudas (lo que debe a otros)
                debts = balance.get('debts', [])
                if debts and len(debts) > 0 and isinstance(debts, list):
                    debts_list = []
                    for d in debts:
                        to_id = d.get('to', 'Desconocido')
                        
                        # Intentar obtener el nombre del acreedor de varias formas
                        to_name = None
                        
                        # Primero intentar con el ID como string
                        if str(to_id) in member_names:
                            to_name = member_names[str(to_id)]
                        
                        # Luego intentar con el ID como número
                        if not to_name and isinstance(to_id, (int, str)):
                            try:
                                numeric_id = int(to_id) if isinstance(to_id, str) else to_id
                                to_name = id_to_name.get(numeric_id)
                            except (ValueError, TypeError):
                                pass
                        
                        # Si aún no tenemos un nombre, usar un valor predeterminado
                        if not to_name:
                            to_name = f"Usuario {to_id}"
                            
                        debts_list.append(f"• Debe a {to_name}: ${d.get('amount', 0):.2f}")
                    debts_text = "\n".join(debts_list)
                else:
                    debts_text = "• No debe a nadie"
                
                # Formatear créditos (lo que le deben)
                credits = balance.get('credits', [])
                if credits and len(credits) > 0 and isinstance(credits, list):
                    credits_list = []
                    for c in credits:
                        from_id = c.get('from', 'Desconocido')
                        
                        # Intentar obtener el nombre del deudor de varias formas
                        from_name = None
                        
                        # Primero intentar con el ID como string
                        if str(from_id) in member_names:
                            from_name = member_names[str(from_id)]
                        
                        # Luego intentar con el ID como número
                        if not from_name and isinstance(from_id, (int, str)):
                            try:
                                numeric_id = int(from_id) if isinstance(from_id, str) else from_id
                                from_name = id_to_name.get(numeric_id)
                            except (ValueError, TypeError):
                                pass
                        
                        # Si aún no tenemos un nombre, usar un valor predeterminado
                        if not from_name:
                            from_name = f"Usuario {from_id}"
                            
                        credits_list.append(f"• Le debe {from_name}: ${c.get('amount', 0):.2f}")
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
                
                # Construir el mensaje completo para este miembro
                member_text = (
                    f"👤 *{member_name}*\n"
                    f"{balance_emoji} Balance neto: ${net_balance:.2f}\n"
                    f"💰 Total a favor: ${balance.get('total_owed', 0):.2f}\n"
                    f"💸 Total a deber: ${balance.get('total_debt', 0):.2f}\n\n"
                    f"*Deudas:*\n{debts_text}\n\n"
                    f"*Créditos:*\n{credits_text}"
                )
                result.append(member_text)
            except Exception as e:
                print(f"Error al formatear balance: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # Si no hay balances formateados, mostrar un mensaje
        if not result:
            return "No hay balances disponibles para mostrar."
        
        return "\n\n" + "\n\n".join(result)
    
    @staticmethod
    def _format_pending_transactions(transactions, member_names):
        """Formatea las transacciones pendientes entre miembros."""
        if not transactions:
            return "No hay transacciones pendientes."
            
        result = []
        for transaction in transactions:
            try:
                from_id = transaction.get('from_member', 'Desconocido')
                to_id = transaction.get('to_member', 'Desconocido')
                amount = transaction.get('amount', 0)
                
                from_name = member_names.get(from_id, f"Usuario {from_id}")
                to_name = member_names.get(to_id, f"Usuario {to_id}")
                
                transaction_text = f"💸 *{from_name}* debe pagar *${amount:.2f}* a *{to_name}*"
                result.append(transaction_text)
            except Exception as e:
                print(f"Error al formatear transacción: {e}")
                continue
                
        if not result:
            return "No hay transacciones pendientes para mostrar."
            
        return "\n\n" + "\n\n".join(result) 