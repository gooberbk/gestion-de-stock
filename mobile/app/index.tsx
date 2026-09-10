import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import { useConnexion } from '../src/contexts/ConnexionContext';

export default function IndexScreen() {
  const router = useRouter();
  const { serverInfo } = useConnexion();

  React.useEffect(() => {
    if (serverInfo) {
      router.replace('/dashboard');
    } else {
      router.replace('/connexion');
    }
  }, [serverInfo, router]);

  return (
    <View style={styles.container}>
      <Text style={styles.text}>Chargement...</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  text: {
    fontSize: 18,
  },
});