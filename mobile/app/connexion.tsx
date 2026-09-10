import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Alert } from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { useConnexion } from '../src/contexts/ConnexionContext';

export default function ConnexionScreen() {
  const { setServerInfo, loadSavedConnection } = useConnexion();
  const [permission, requestPermission] = useCameraPermissions();
  const [scanned, setScanned] = useState(false);

  useEffect(() => {
    loadSavedConnection();
  }, []);

  if (!permission) {
    return <View />;
  }

  if (!permission.granted) {
    return (
      <View style={styles.container}>
        <Text style={styles.message}>Nous avons besoin de votre permission pour utiliser la caméra</Text>
        <TouchableOpacity onPress={requestPermission} style={styles.button}>
          <Text style={styles.buttonText}>Accorder la permission</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const handleBarCodeScanned = ({ data }: { data: string }) => {
    if (scanned) return;
    setScanned(true);

    try {
      const connexionData = JSON.parse(data);
      if (connexionData.ip && connexionData.port) {
        setServerInfo({ ip: connexionData.ip, port: connexionData.port });
        Alert.alert('Connexion réussie', 'Vous êtes maintenant connecté au serveur');
      } else {
        Alert.alert('Erreur', 'QR code invalide');
        setScanned(false);
      }
    } catch (error) {
      Alert.alert('Erreur', 'QR code invalide');
      setScanned(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Scanner le QR code de connexion</Text>
      <Text style={styles.subtitle}>Scannez le QR code affiché sur le serveur</Text>
      
      <View style={styles.cameraContainer}>
        <CameraView
          style={styles.camera}
          onBarcodeScanned={scanned ? undefined : handleBarCodeScanned}
          barcodeScannerSettings={{
            barcodeTypes: ['qr'],
          }}
        />
      </View>

      {scanned && (
        <TouchableOpacity 
          style={styles.button} 
          onPress={() => setScanned(false)}
        >
          <Text style={styles.buttonText}>Scanner à nouveau</Text>
        </TouchableOpacity>
      )}
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
  message: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 20,
  },
  cameraContainer: {
    width: 300,
    height: 300,
    borderRadius: 10,
    overflow: 'hidden',
    marginBottom: 30,
  },
  camera: {
    flex: 1,
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 10,
    minWidth: 200,
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
  },
});