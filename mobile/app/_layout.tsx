import React from 'react';
import { Stack } from 'expo-router';
import { ConnexionProvider } from '../src/contexts/ConnexionContext';

export default function RootLayout() {
  return (
    <ConnexionProvider>
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="index" options={{ headerShown: false }} />
        <Stack.Screen name="connexion" options={{ headerShown: false }} />
        <Stack.Screen name="dashboard" options={{ headerShown: false }} />
        <Stack.Screen name="historique" options={{ headerShown: false }} />
      </Stack>
    </ConnexionProvider>
  );
}