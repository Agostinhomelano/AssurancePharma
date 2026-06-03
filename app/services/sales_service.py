"""
Service pour la gestion des ventes
"""

from datetime import datetime, timedelta
from app import db
from app.models import Sale, SaleItem, Medicine
from app.services.activity_service import ActivityService

class SalesService:
    """Service pour les ventes"""
    
    @staticmethod
    def create_sale(employee_id, items, payment_method):
        """
        Crée une nouvelle vente
        
        Args:
            employee_id: ID de l'employé
            items: Liste des items [{'medicine_id': int, 'quantity': int}, ...]
            payment_method: Méthode de paiement (Espèces, Mobile Money, Carte)
        
        Returns:
            Objet Sale ou None en cas d'erreur
        """
        try:
            sale = Sale(
                employee_id=employee_id,
                payment_method=payment_method
            )
            
            total_amount = 0
            total_cost = 0
            
            for item in items:
                medicine = Medicine.query.get(item['medicine_id'])
                if not medicine:
                    raise ValueError(f"Médicament {item['medicine_id']} introuvable")
                
                if medicine.quantite < item['quantity']:
                    raise ValueError(f"Stock insuffisant pour {medicine.nom}")
                
                # Créer le SaleItem
                sale_item = SaleItem(
                    sale=sale,
                    medicine_id=item['medicine_id'],
                    quantity=item['quantity'],
                    unit_price=medicine.prix_vente,
                    unit_cost=medicine.prix_achat
                )
                
                total_amount += medicine.prix_vente * item['quantity']
                total_cost += medicine.prix_achat * item['quantity']
                
                # Réduire le stock
                medicine.quantite -= item['quantity']
                
                db.session.add(sale_item)
            
            sale.total_amount = total_amount
            sale.total_cost = total_cost
            sale.profit = total_amount - total_cost
            
            db.session.add(sale)
            db.session.commit()

            return sale
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la création de la vente: {e}")
            return None
    
    @staticmethod
    def get_daily_sales(date=None):
        """
        Récupère les ventes d'un jour
        
        Args:
            date: Date (par défaut aujourd'hui)
        
        Returns:
            Liste des ventes du jour
        """
        if date is None:
            date = datetime.now().date()
        
        return Sale.query.filter(
            db.func.date(Sale.created_at) == date
        ).all()
    
    @staticmethod
    def get_sales_summary(start_date=None, end_date=None):
        """
        Récupère un résumé des ventes pour une période
        
        Args:
            start_date: Date de début
            end_date: Date de fin
        
        Returns:
            Dict avec les statistiques
        """
        if start_date is None:
            start_date = datetime.now().date() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.now().date()
        
        sales = Sale.query.filter(
            Sale.created_at >= datetime.combine(start_date, datetime.min.time()),
            Sale.created_at <= datetime.combine(end_date, datetime.max.time())
        ).all()
        
        return {
            'total_sales': len(sales),
            'total_amount': sum(s.total_amount for s in sales),
            'total_cost': sum(s.total_cost for s in sales),
            'total_profit': sum(s.profit for s in sales),
            'average_sale': sum(s.total_amount for s in sales) / len(sales) if sales else 0
        }
    
    @staticmethod
    def get_best_selling_medicines(limit=5, days=30):
        """
        Récupère les meilleures ventes
        
        Args:
            limit: Nombre de résultats
            days: Nombre de jours à considérer
        
        Returns:
            Liste des meilleures ventes
        """
        start_date = datetime.now() - timedelta(days=days)
        
        medicines = db.session.query(
            Medicine,
            db.func.sum(SaleItem.quantity).label('total_quantity'),
            db.func.sum(SaleItem.quantity * SaleItem.unit_price).label('total_amount')
        ).join(SaleItem).join(Sale).filter(
            Sale.created_at >= start_date
        ).group_by(Medicine.id).order_by(
            db.desc('total_quantity')
        ).limit(limit).all()
        
        return medicines
