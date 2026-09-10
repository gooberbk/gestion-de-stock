import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator } from 'react-native';
import { useConnexion } from '../src/contexts/ConnexionContext';

interface Transaction {
  transaction_id: number;
  produit_id: number;
  produit_nom: string;
  produit_code_qr: string;
  quantite_vendue: number;
  prix_vente_effectif: number;
  marge_totale: number;
  date_transaction: string;
  stock_negatif: boolean;
}

export default function HistoriqueScreen() {
  const { serverInfo } = useConnexion();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTransactions();
  }, [serverInfo]);

  const loadTransactions = async () => {
    if (!serverInfo) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://${serverInfo.ip}:${serverInfo.port}/transactions?limite=50`);
      if (!response.ok) {
        throw new Error('Erreur lors du chargement des transactions');
      }
      const data = await response.json();
      setTransactions(data.transactions);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur inconnue');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Chargement...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>{error}</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Historique des transactions</Text>
      </View>

      {transactions.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>Aucune transaction enregistrée</Text>
        </View>
      ) : (
        transactions.map((transaction) => (
          <View key={transaction.transaction_id} style={styles.transactionCard}>
            <View style={styles.transactionHeader}>
              <Text style={styles.productName}>{transaction.produit_nom}</Text>
              <Text style={styles.transactionDate}>
                {new Date(transaction.date_transaction).toLocaleString('fr-FR')}
              </Text>
            </View>
            
            <View style={styles.transactionDetails}>
              <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>Quantité:</Text>
                <Text style={styles.detailValue}>{transaction.quantite_vendue}</Text>
              </View>
              <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>Prix vente:</Text>
                <Text style={styles.detailValue}>{transaction.prix_vente_effectif.toFixed(2)} €</Text>
              </View>
              <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>Marge:</Text>
                <Text style={[styles.detailValue, styles.margeValue]}>
                  {transaction.marge_totale.toFixed(2)} €
                </Text>
              </View>
            </View>

            {transaction.stock_negatif && (
              <View style={styles.alertContainer}>
                <Text style={styles.alertText}>⚠️ Stock négatif lors de cette vente</Text>
              </View>
            )}
          </View>
        ))
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  loadingText: {
    marginTop: 10,
    color: '#666',
  },
  errorText: {
    fontSize: 16,
    color: '#FF3B30',
    textAlign: 'center',
    marginTop: 50,
  },
  emptyContainer: {
    padding: 40,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 16,
    color: '#999',
  },
  transactionCard: {
    backgroundColor: '#fff',
    margin: 15,
    padding: 15,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  transactionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  productName: {
    fontSize: 18,
    fontWeight: 'bold',
    flex: 1,
  },
  transactionDate: {
    fontSize: 12,
    color: '#666',
  },
  transactionDetails: {
    marginBottom: 10,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 5,
  },
  detailLabel: {
    fontSize: 14,
    color: '#666',
  },
  detailValue: {
    fontSize: 14,
    fontWeight: '500',
  },
  margeValue: {
    color: '#34C759',
    fontWeight: 'bold',
  },
  alertContainer: {
    backgroundColor: '#FFF3F3',
    padding: 8,
    borderRadius: 5,
    marginTop: 5,
  },
  alertText: {
    fontSize: 12,
    color: '#FF3B30',
    fontWeight: 'bold',
  },
});