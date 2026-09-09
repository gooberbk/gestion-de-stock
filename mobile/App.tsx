import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { ConnexionProvider } from './src/contexts/ConnexionContext';
import ConnexionScreen from './src/screens/ConnexionScreen';
import DashboardScreen from './src/screens/DashboardScreen';
import HistoriqueScreen from './src/screens/HistoriqueScreen';

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <ConnexionProvider>
      <NavigationContainer>
        <Stack.Navigator screenOptions={{ headerShown: false }}>
          <Stack.Screen name="connexion" component={ConnexionScreen} />
          <Stack.Screen name="dashboard" component={DashboardScreen} />
          <Stack.Screen name="historique" component={HistoriqueScreen} />
        </Stack.Navigator>
      </NavigationContainer>
    </ConnexionProvider>
  );
}
