import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, RefreshControl, TouchableOpacity, Dimensions } from 'react-native';
import { useRouter } from 'expo-router';
import { BarChart } from 'react-native-chart-kit';
import { useConnexion } from '../src/contexts/ConnexionContext';

interface VenteEvent {
  type: string;
  produit_id: number;
  produit_nom: string;
  produit_code_qr: string;
  quantite_vendue: number;
  nouveau_stock: number;
  marge: number;
  stock_negatif: boolean;
  transaction_id: number;
}

interface MargeJourEvent {
  type: string;
  date: string;
  total_marge: number;
  total_ca: number;
  nombre_ventes: number;
}

interface HourlySales {
  hour: string;
  sales: number;
}

export default function DashboardScreen() {
  const router = useRouter();
  const { serverInfo, disconnect } = useConnexion();
  const [stats, setStats] = useState({
    total_marge: 0,
    total_ca: 0,
    nombre_ventes: 0,
  });
  const [recentSales, setRecentSales] = useState<VenteEvent[]>([]);
  const [hourlySales, setHourlySales] = useState<HourlySales[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');
  const [ws, setWs] = useState<WebSocket | null>(null);

  const screenWidth = Dimensions.get('window').width;

  useEffect(() => {
    if (!serverInfo) {
      setConnectionStatus('disconnected');
      return;
    }

    setConnectionStatus('connecting');
    connectWebSocket();
    loadInitialData();

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [serverInfo]);

  const loadInitialData = async () => {
    if (!serverInfo) return;

    try {
      const statsResponse = await fetch(`http://${serverInfo.ip}:${serverInfo.port}/statistiques/jour`);
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStats({
          total_marge: statsData.total_marge,
          total_ca: statsData.total_ca,
          nombre_ventes: statsData.nombre_ventes,
        });
        
        if (statsData.dernieres_ventes && statsData.dernieres_ventes.length > 0) {
          const ventesFormatees = statsData.dernieres_ventes.map((v: any) => ({
            type: 'vente',
            produit_id: v.produit_id,
            produit_nom: v.produit_nom,
            produit_code_qr: v.produit_code_qr,
            quantite_vendue: v.quantite_vendue,
            nouveau_stock: 0,
            marge: v.marge,
            stock_negatif: false,
            transaction_id: v.transaction_id,
          }));
          setRecentSales(ventesFormatees);
        }
      }
    } catch (error) {
      console.error('Erreur lors du chargement des données initiales:', error);
    }
  };

  const connectWebSocket = () => {
    if (!serverInfo) return;

    const wsUrl = `ws://${serverInfo.ip}:${serverInfo.port}/ws`;
    const websocket = new WebSocket(wsUrl);

    websocket.onopen = () => {
      console.log('WebSocket connecté');
      setConnectionStatus('connected');
      setWs(websocket);
    };

    websocket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        
        if (message.type === 'marge_du_jour') {
          setStats({
            total_marge: message.total_marge,
            total_ca: message.total_ca,
            nombre_ventes: message.nombre_ventes,
          });
        } else if (message.type === 'vente') {
          const venteEvent = message as VenteEvent;
          setRecentSales((prev) => [venteEvent, ...prev].slice(0, 5));
          
          const currentHour = new Date().getHours();
          setHourlySales((prev) => {
            const updated = [...prev];
            const hourIndex = updated.findIndex(h => h.hour === currentHour.toString());
            if (hourIndex >= 0) {
              updated[hourIndex].sales += venteEvent.quantite_vendue;
            } else {
              updated.push({ hour: currentHour.toString(), sales: venteEvent.quantite_vendue });
            }
            return updated.sort((a, b) => parseInt(a.hour) - parseInt(b.hour));
          });
        }
      } catch (error) {
        console.error('Erreur parsing message WebSocket:', error);
      }
    };

    websocket.onerror = (error) => {
      console.error('Erreur WebSocket:', error);
      setConnectionStatus('disconnected');
    };

    websocket.onclose = () => {
      console.log('WebSocket déconnecté');
      setConnectionStatus('disconnected');
      setTimeout(connectWebSocket, 5000);
    };
  };

  const handleDisconnect = () => {
    if (ws) {
      ws.close();
    }
    disconnect();
  };

  if (connectionStatus === 'disconnected') {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>Déconnecté du serveur</Text>
        <Text style={styles.subText}>Tentative de reconnexion en cours...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} refreshControl={
      <RefreshControl refreshing={connectionStatus === 'connecting'} onRefresh={connectWebSocket} />
    }>
      <View style={styles.header}>
        <Text style={styles.title}>Dashboard</Text>
        <View style={styles.headerButtons}>
          <TouchableOpacity onPress={() => router.push('/historique')} style={styles.headerButton}>
            <Text style={styles.headerButtonText}>Historique</Text>
          </TouchableOpacity>
          <TouchableOpacity onPress={handleDisconnect} style={styles.disconnectButton}>
            <Text style={styles.disconnectButtonText}>Déconnecter</Text>
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <Text style={styles.statLabel}>Chiffre d'affaires</Text>
          <Text style={styles.statValue}>{stats.total_ca.toFixed(2)} €</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statLabel}>Marge totale</Text>
          <Text style={styles.statValue}>{stats.total_marge.toFixed(2)} €</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statLabel}>Nombre de ventes</Text>
          <Text style={styles.statValue}>{stats.nombre_ventes}</Text>
        </View>
      </View>

      <View style={styles.chartContainer}>
        <Text style={styles.sectionTitle}>Ventes par heure</Text>
        {hourlySales.length > 0 ? (
          <BarChart
            data={{
              labels: hourlySales.map(h => `${h.hour}h`),
              datasets: [{
                data: hourlySales.map(h => h.sales)
              }]
            }}
            width={screenWidth - 40}
            height={220}
            yAxisLabel=""
            chartConfig={{
              backgroundColor: '#1e2923',
              backgroundGradientFrom: '#08130D',
              backgroundGradientTo: '#1f2937',
              decimalPlaces: 0,
              color: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`,
              labelColor: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`,
              style: {
                borderRadius: 16
              }
            }}
            style={{
              marginVertical: 8,
              borderRadius: 16
            }}
          />
        ) : (
          <Text style={styles.emptyText}>Pas encore de données pour le graphique</Text>
        )}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Dernières ventes</Text>
        {recentSales.length === 0 ? (
          <Text style={styles.emptyText}>Aucune vente aujourd'hui</Text>
        ) : (
          recentSales.map((sale) => (
            <View key={sale.transaction_id} style={[
              styles.saleCard,
              sale.stock_negatif && styles.alertCard
            ]}>
              <Text style={styles.saleProduct}>{sale.produit_nom}</Text>
              <Text style={styles.saleDetails}>
                {sale.quantite_vendue} x {sale.marge.toFixed(2)} € marge
              </Text>
              {sale.stock_negatif && (
                <View style={styles.alertBadge}>
                  <Text style={styles.alertBadgeText}>⚠️ Stock négatif ({sale.nouveau_stock})</Text>
                </View>
              )}
            </View>
          ))
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#fff',
  },
  headerButtons: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  headerButton: {
    backgroundColor: '#007AFF',
    padding: 8,
    borderRadius: 5,
    marginRight: 10,
  },
  headerButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  disconnectButton: {
    backgroundColor: '#FF3B30',
    padding: 8,
    borderRadius: 5,
  },
  disconnectButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    padding: 20,
  },
  statCard: {
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 10,
    width: '30%',
    alignItems: 'center',
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 5,
  },
  statValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#007AFF',
  },
  section: {
    padding: 20,
  },
  chartContainer: {
    padding: 20,
    backgroundColor: '#fff',
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
  },
  emptyText: {
    color: '#999',
    textAlign: 'center',
    padding: 20,
  },
  saleCard: {
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
  },
  alertCard: {
    borderWidth: 2,
    borderColor: '#FF3B30',
    backgroundColor: '#FFF3F3',
  },
  alertBadge: {
    backgroundColor: '#FF3B30',
    padding: 5,
    borderRadius: 5,
    marginTop: 5,
    alignSelf: 'flex-start',
  },
  alertBadgeText: {
    color: 'white',
    fontSize: 12,
    fontWeight: 'bold',
  },
  saleProduct: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  saleDetails: {
    fontSize: 14,
    color: '#666',
  },
  errorText: {
    fontSize: 18,
    color: '#FF3B30',
    textAlign: 'center',
    marginTop: 50,
  },
  subText: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
  },
});