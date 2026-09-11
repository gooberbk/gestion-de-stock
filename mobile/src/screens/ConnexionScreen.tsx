import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Alert, TextInput } from 'react-native';
import { useConnexion } from '../contexts/ConnexionContext';

export default function ConnexionScreen({ navigation }: any) {
  const { setServerInfo, loadSavedConnection, serverInfo } = useConnexion();
  const [ip, setIp] = useState('192.168.1.80');
  const [port, setPort] = useState('8000');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Charger la connexion sauvegardée au démarrage
    loadSavedConnection();
  }, []);

  useEffect(() => {
    // Si déjà connecté, naviguer vers le dashboard
    if (serverInfo) {
      navigation.navigate('dashboard');
    }
  }, [serverInfo, navigation]);

  const handleConnect = async () => {
    if (!ip || !port) {
      Alert.alert('Erreur', 'Veuillez remplir l\'IP et le port');
      return;
    }

    setLoading(true);

    try {
      // Tester la connexion
      const response = await fetch(`http://${ip}:${port}/health`);
      if (response.ok) {
        setServerInfo({ ip, port: parseInt(port) });
        Alert.alert('Connexion réussie', 'Vous êtes maintenant connecté au serveur');
      } else {
        Alert.alert('Erreur', 'Impossible de se connecter au serveur');
      }
    } catch (error) {
      Alert.alert('Erreur', 'Impossible de se connecter au serveur');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Connexion au serveur</Text>
      <Text style={styles.subtitle}>Entrez l'adresse IP et le port du serveur</Text>

      <View style={styles.inputContainer}>
        <Text style={styles.label}>Adresse IP</Text>
        <TextInput
          style={styles.input}
          value={ip}
          onChangeText={setIp}
          placeholder="192.168.1.x"
          keyboardType="numeric"
          autoCapitalize="none"
        />
      </View>

      <View style={styles.inputContainer}>
        <Text style={styles.label}>Port</Text>
        <TextInput
          style={styles.input}
          value={port}
          onChangeText={setPort}
          placeholder="8000"
          keyboardType="numeric"
        />
      </View>

      <TouchableOpacity
        style={[styles.button, loading && styles.buttonDisabled]}
        onPress={handleConnect}
        disabled={loading}
      >
        <Text style={styles.buttonText}>
          {loading ? 'Connexion...' : 'Se connecter'}
        </Text>
      </TouchableOpacity>

      <Text style={styles.hint}>
        💡 Pour trouver l'IP de votre PC :{`\n`}
        • Windows : ipconfig{`\n`}
        • Linux/Mac : ifconfig ou ip addr
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 30,
    textAlign: 'center',
  },
  inputContainer: {
    width: '100%',
    marginBottom: 20,
  },
  label: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
    color: '#333',
  },
  input: {
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 15,
    fontSize: 16,
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 10,
    minWidth: 200,
    marginTop: 10,
  },
  buttonDisabled: {
    backgroundColor: '#ccc',
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  hint: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
    marginTop: 30,
    lineHeight: 18,
  },
});