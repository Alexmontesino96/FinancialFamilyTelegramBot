"""
Messages en Français

Ce fichier contient tous les textes affichés par le bot en français.
"""

class Messages:
    """Messages formatés pour Telegram en Français."""
    
    # Messages de bienvenue
    WELCOME = (
        "👋 Bienvenue sur le Bot de Gestion Familiale !\n"
        "Ce bot vous aide à gérer les dépenses partagées avec votre famille ou groupe d'amis.\n"
        "Que souhaitez-vous faire ?"
    )
    
    MAIN_MENU = "✨ Bienvenue sur votre tableau de bord familial !\nChoisissez une option :"
    
    # Messages d'erreur
    ERROR_NOT_IN_FAMILY = "❌ Vous n'êtes dans aucune famille. Utilisez /start pour créer ou rejoindre une famille."
    ERROR_FAMILY_NOT_FOUND = "❌ Famille non trouvée. Elle a peut-être été supprimée."
    ERROR_INVALID_OPTION = "❌ Option non valide. Veuillez sélectionner une option du menu."
    ERROR_API = "❌ Erreur de communication avec l'API. Veuillez réessayer plus tard."
    ERROR_INVALID_AMOUNT = "❌ Montant non valide. Veuillez entrer un nombre positif."
    ERROR_CREATING_EXPENSE = "❌ Erreur lors de la création de la dépense. Veuillez réessayer plus tard."
    ERROR_MEMBER_NOT_FOUND = "❌ Vos informations de membre n'ont pas été trouvées. Veuillez réessayer."
    ERROR_NO_EXPENSES = "❌ Il n'y a pas de dépenses enregistrées à afficher."
    ERROR_NO_PAYMENTS = "❌ Il n'y a pas de paiements enregistrés à afficher."
    ERROR_EXPENSE_NOT_FOUND = "❌ La dépense spécifiée n'a pas été trouvée."
    ERROR_PAYMENT_NOT_FOUND = "❌ Le paiement spécifié n'a pas été trouvé."
    ERROR_DELETING_EXPENSE = "❌ Erreur lors de la suppression de la dépense. Veuillez réessayer plus tard."
    ERROR_DELETING_PAYMENT = "❌ Erreur lors de la suppression du paiement. Veuillez réessayer plus tard."
    ERROR_UPDATING_EXPENSE = "❌ Erreur lors de la mise à jour de la dépense. Veuillez réessayer plus tard."
    
    # Messages de succès
    SUCCESS_FAMILY_CREATED = "✅ Famille '{name}' créée avec succès.\n*ID :* `{id}`"
    SUCCESS_JOINED_FAMILY = "🎉 Vous avez rejoint la famille *{family_name}* avec succès !"
    SUCCESS_EXPENSE_CREATED = "✅ Dépense créée avec succès !"
    SUCCESS_PAYMENT_CREATED = "✅ Paiement enregistré avec succès !"
    SUCCESS_EXPENSE_DELETED = "✅ Dépense supprimée avec succès."
    SUCCESS_PAYMENT_DELETED = "✅ Paiement supprimé avec succès."
    SUCCESS_EXPENSE_UPDATED = "✅ Dépense mise à jour avec succès."
    
    # Messages de flux de création de famille
    CREATE_FAMILY_INTRO = "🏠 Créons une nouvelle famille.\n\n" \
                         "Comment s'appellera votre famille ?"
    
    CREATE_FAMILY_NAME_RECEIVED = "👍 Nom de famille reçu : *{family_name}*\n\n" \
                                 "Maintenant, quel est votre nom ? C'est ainsi que les autres membres vous identifieront."
    
    # Messages de flux pour rejoindre une famille
    JOIN_FAMILY_INTRO = "🔗 Rejoignons une famille existante.\n\n" \
                       "Veuillez entrer l'ID de la famille que vous souhaitez rejoindre :"
    
    JOIN_FAMILY_NAME_PROMPT = "👍 Code de famille valide.\n\n" \
                             "Quel est votre nom ? C'est ainsi que les autres membres vous identifieront."
    
    JOIN_FAMILY_SUCCESS = "✅ Vous avez rejoint la famille *{family_name}* avec succès !"
    
    # Messages de flux de dépenses
    CREATE_EXPENSE_INTRO = "💸 Créons une nouvelle dépense.\n\n" \
                          "Quelle est la description de la dépense ? (Ex : Supermarché, Dîner, etc.)"
    
    CREATE_EXPENSE_AMOUNT = "👍 Description reçue : *{description}*\n\n" \
                           "Maintenant, quel est le montant de la dépense ? (Ex : 100.50)"
    
    CREATE_EXPENSE_DIVISION = "👍 Montant reçu : *${amount:.2f}*\n\n" \
                             "Comment voulez-vous partager cette dépense ?"
    
    CREATE_EXPENSE_SELECT_MEMBERS = "👥 Sélectionnez les membres qui partageront cette dépense :\n\n" \
                                   "Appuyez sur un nom pour sélectionner/désélectionner\n" \
                                   "- Les noms avec ✅ sont sélectionnés\n" \
                                   "- Les noms avec ⬜ ne sont pas sélectionnés\n\n" \
                                   "Lorsque vous avez terminé, appuyez sur \"✓ Continuer\""
    
    CREATE_EXPENSE_CONFIRM = "📝 Résumé de la dépense :\n\n" \
                            "*Description :* {description}\n" \
                            "*Montant :* ${amount:.2f}\n" \
                            "*Payé par :* {paid_by}\n" \
                            "*Partagé entre :* {split_among}\n\n" \
                            "Confirmez-vous cette dépense ?"
    
    # Messages pour lister les dépenses
    EXPENSES_LIST_HEADER = "📋 *Liste des Dépenses*\n\n"
    
    EXPENSE_LIST_ITEM = (
        "*Description :* {description}\n"
        "*Montant :* {amount}\n"
        "*Payé par :* {paid_by}\n"
        "*Date :* {date}\n"
        "----------------------------\n\n"
    )
    
    # Messages pour lister les paiements
    PAYMENTS_LIST_HEADER = "💳 *Liste des Paiements*\n\n"
    
    PAYMENT_LIST_ITEM = (
        "*De :* {from_member}\n"
        "*À :* {to_member}\n"
        "*Montant :* {amount}\n"
        "*Date :* {date}\n"
        "----------------------------\n\n"
    )
    
    # Messages pour dépenses et paiements non trouvés
    NO_EXPENSES = "📋 Il n'y a pas de dépenses enregistrées dans cette famille."
    NO_PAYMENTS = "💳 Il n'y a pas de paiements enregistrés dans cette famille."
    
    # Messages de flux de paiements
    CREATE_PAYMENT_INTRO = "💳 Enregistrons un nouveau paiement.\n\n" \
                          "À qui payez-vous ?"
    
    NO_DEBTS = "✅ *Félicitations !* En ce moment, vous n'avez aucune dette en suspens avec un membre de votre famille."
    
    SELECT_PAYMENT_RECIPIENT = "💳 À qui voulez-vous payer ? Sélectionnez un membre de votre famille à qui vous devez de l'argent :"
    
    CREATE_PAYMENT_AMOUNT = "👍 Destinataire sélectionné : *{to_member}*\n\n" \
                           "Maintenant, quel est le montant du paiement ? (Ex : 100.50)"
    
    CREATE_PAYMENT_CONFIRM = "📝 Résumé du paiement :\n\n" \
                            "*De :* {from_member}\n" \
                            "*À :* {to_member}\n" \
                            "*Montant :* ${amount:.2f}\n\n" \
                            "Confirmez-vous ce paiement ?"
    
    # Messages de modification/suppression
    EDIT_OPTIONS = "✏️ Que souhaitez-vous faire ?"
    
    SELECT_EXPENSE_TO_EDIT = "📝 Sélectionnez la dépense que vous souhaitez modifier :"
    SELECT_EXPENSE_TO_DELETE = "🗑️ Sélectionnez la dépense que vous souhaitez supprimer :"
    
    SELECT_PAYMENT_TO_EDIT = "📝 Sélectionnez le paiement que vous souhaitez modifier :"
    SELECT_PAYMENT_TO_DELETE = "🗑️ Sélectionnez le paiement que vous souhaitez supprimer :"
    
    CONFIRM_DELETE_EXPENSE = "⚠️ Êtes-vous sûr de vouloir supprimer cette dépense ?\n\n{details}"
    CONFIRM_DELETE_PAYMENT = "⚠️ Êtes-vous sûr de vouloir supprimer ce paiement ?\n\n{details}"
    
    EDIT_EXPENSE_AMOUNT = "📝 Entrez le nouveau montant pour la dépense :\n\n{details}"
    
    # Messages supplémentaires pour la modification/suppression
    INVALID_EDIT_OPTION = "❌ Option de modification non valide. Veuillez sélectionner une option du menu."
    NO_EXPENSES_TO_EDIT = "❌ Il n'y a pas de dépenses enregistrées à modifier."
    NO_EXPENSES_TO_DELETE = "❌ Il n'y a pas de dépenses enregistrées à supprimer."
    NO_PAYMENTS_TO_DELETE = "❌ Il n'y a pas de paiements enregistrés à supprimer."
    NO_PAYMENTS_TO_EDIT = "❌ Il n'y a pas de paiements enregistrés à modifier."
    ITEM_NOT_FOUND = "❌ L'élément sélectionné n'a pas été trouvé."
    
    # Messages généraux
    CANCEL_OPERATION = "❌ Opération annulée."
    LOADING = "⏳ Chargement..."
    FAMILY_INFO = "ℹ️ *Informations sur la famille*\n\n*Nom :* {name}\n*ID de Famille :* `{id}`\n*Membres :* {members_count}\n\n*Membres :*\n{members_list}"
    FAMILY_INVITATION = "🔗 *Invitation à la famille*\n\n*Nom :* {name}\n*ID :* `{id}`\n\nPartagez cet ID avec les personnes que vous souhaitez inviter dans votre famille."
    UNKNOWN_COMMAND = "Je ne comprends pas cette commande. Voici le menu principal :"
    
    # Messages pour les soldes
    BALANCES_HEADER = "💰 *Soldes de la famille*\n\n"
    BALANCE_SUMMARY = "\n\n📊 *Résumé de votre solde :*\n"
    YOU_OWE = "💸 *Vous devez :* ${amount:.2f} au total\n"
    OWE_TO = "└ À {name} : ${amount:.2f}\n"
    LARGEST_DEBT = "└ Plus grande dette envers {name} : ${amount:.2f}\n"
    NO_DEBT = "💸 *Vous ne devez d'argent à personne*\n"
    OWED_TO_YOU = "💰 *On vous doit :* ${amount:.2f} au total\n"
    FROM_USER = "└ {name} : ${amount:.2f}\n"
    LARGEST_CREDIT = "└ Plus grand crédit de {name} : ${amount:.2f}\n"
    NO_CREDIT = "💰 *Personne ne vous doit d'argent*\n"
    
    # Messages pour partager une invitation
    SHARE_INVITATION_INTRO = "🔗 Partagez ce lien pour inviter quelqu'un à rejoindre votre famille :"
    
    SHARE_INVITATION_ID = "📝 ID de famille : `{family_id}`\n\nPartagez cet ID avec qui vous voulez qui rejoigne votre famille."
    
    SHARE_INVITATION_QR = "Ils peuvent également scanner ce code QR :"
    
    # Message pour le lien d'invitation
    INVITATION_LINK = (
        "🔗 *Invitation à la Famille*\n\n"
        "Partagez ce code QR ou le lien suivant pour inviter quelqu'un à rejoindre votre famille :\n\n"
        "`{invite_link}`\n\n"
        "Instructions pour l'invité :\n"
        "1. Cliquez sur le lien ou scannez le code QR\n"
        "2. Le bot s'ouvrira\n"
        "3. Appuyez sur le bouton 'DÉMARRER' ou envoyez /start\n"
        "4. Vous serez automatiquement ajouté à la famille"
    )
    
    # Messages spécifiques au système de langues
    LANGUAGE_SELECTION = "🌍 Sélectionnez votre langue préférée :"
    LANGUAGE_UPDATED = "✅ Langue mise à jour en Français !"
    
    # Messages pour les claviers
    KB_VIEW_BALANCES = "💰 Voir Soldes"
    KB_CREATE_EXPENSE = "💸 Créer Dépense"
    KB_LIST_RECORDS = "📜 Lister Enregistrements"
    KB_REGISTER_PAYMENT = "💳 Enregistrer Paiement"
    KB_EDIT_DELETE = "✏️ Modifier/Supprimer"
    KB_FAMILY_INFO = "ℹ️ Info Famille"
    KB_SHARE_INVITATION = "🔗 Partager Invitation"
    KB_CHANGE_LANGUAGE = "🌍 Changer Langue"
    KB_EDIT_EXPENSES = "📝 Modifier Dépenses"
    KB_DELETE_EXPENSES = "🗑️ Supprimer Dépenses"
    KB_EDIT_PAYMENTS = "📝 Modifier Paiements"
    KB_DELETE_PAYMENTS = "🗑️ Supprimer Paiements"
    KB_BACK_TO_MENU = "↩️ Retour au Menu"
    KB_CREATE_FAMILY = "🏠 Créer Famille"
    KB_JOIN_FAMILY = "🔗 Rejoindre Famille"
    KB_CONFIRM = "✅ Confirmer"
    KB_CANCEL = "❌ Annuler"
    KB_LIST_EXPENSES = "📋 Lister Dépenses"
    KB_LIST_PAYMENTS = "📊 Lister Paiements"
    
    # Messages pour lister les enregistrements
    LIST_RECORDS_TITLE = "📜 *Lister les Enregistrements*\n\n"
    WHAT_RECORDS_TO_VIEW = "Quels enregistrements souhaitez-vous consulter ?"
    ERROR_LISTING_OPTIONS = "Erreur lors de l'affichage des options de liste. Veuillez réessayer."
    ERROR_PROCESSING_OPTION = "Erreur lors du traitement de l'option sélectionnée. Veuillez réessayer."
    
    # Messages pour les soldes
    BALANCES_HEADER = "💰 *Soldes de la famille*\n\n"
    BALANCE_SUMMARY = "\n\n📊 *Résumé de votre solde :*\n"
    YOU_OWE = "💸 *Vous devez :* ${amount:.2f} au total\n"
    OWE_TO = "└ À {name} : ${amount:.2f}\n"
    LARGEST_DEBT = "└ Plus grande dette envers {name} : ${amount:.2f}\n"
    NO_DEBT = "💸 *Vous ne devez d'argent à personne*\n"
    OWED_TO_YOU = "💰 *On vous doit :* ${amount:.2f} au total\n"
    FROM_USER = "└ {name} : ${amount:.2f}\n"
    LARGEST_CREDIT = "└ Plus grand crédit de {name} : ${amount:.2f}\n"
    NO_CREDIT = "💰 *Personne ne vous doit d'argent*\n"
    
    # Messages pour partager une invitation
    SHARE_INVITATION_INTRO = "🔗 Partagez ce lien pour inviter quelqu'un à rejoindre votre famille :"
    
    SHARE_INVITATION_ID = "📝 ID de famille : `{family_id}`\n\nPartagez cet ID avec qui vous voulez qui rejoigne votre famille."
    
    SHARE_INVITATION_QR = "Ils peuvent également scanner ce code QR :"
    
    # Message pour le lien d'invitation
    INVITATION_LINK = (
        "🔗 *Invitation à la Famille*\n\n"
        "Partagez ce code QR ou le lien suivant pour inviter quelqu'un à rejoindre votre famille :\n\n"
        "`{invite_link}`\n\n"
        "Instructions pour l'invité :\n"
        "1. Cliquez sur le lien ou scannez le code QR\n"
        "2. Le bot s'ouvrira\n"
        "3. Appuyez sur le bouton 'DÉMARRER' ou envoyez /start\n"
        "4. Vous serez automatiquement ajouté à la famille"
    )
    
    # Messages spécifiques au système de langues
    LANGUAGE_SELECTION = "🌍 Sélectionnez votre langue préférée :"
    LANGUAGE_UPDATED = "✅ Langue mise à jour en Français !"
    
    # Messages pour les claviers
    KB_VIEW_BALANCES = "💰 Voir Soldes"
    KB_CREATE_EXPENSE = "💸 Créer Dépense"
    KB_LIST_RECORDS = "📜 Lister Enregistrements"
    KB_REGISTER_PAYMENT = "💳 Enregistrer Paiement"
    KB_EDIT_DELETE = "✏️ Modifier/Supprimer"
    KB_FAMILY_INFO = "ℹ️ Info Famille"
    KB_SHARE_INVITATION = "🔗 Partager Invitation"
    KB_CHANGE_LANGUAGE = "🌍 Changer Langue"
    KB_EDIT_EXPENSES = "📝 Modifier Dépenses"
    KB_DELETE_EXPENSES = "🗑️ Supprimer Dépenses"
    KB_EDIT_PAYMENTS = "📝 Modifier Paiements"
    KB_DELETE_PAYMENTS = "🗑️ Supprimer Paiements"
    KB_BACK_TO_MENU = "↩️ Retour au Menu"
    KB_CREATE_FAMILY = "🏠 Créer Famille"
    KB_JOIN_FAMILY = "🔗 Rejoindre Famille"
    KB_CONFIRM = "✅ Confirmer"
    KB_CANCEL = "❌ Annuler"
    KB_LIST_EXPENSES = "📋 Lister Dépenses"
    KB_LIST_PAYMENTS = "📊 Lister Paiements" 