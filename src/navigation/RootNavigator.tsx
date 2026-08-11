/**
 * Root Navigator — Bottom Tabs + Stack.
 */

import React from 'react';
import { Text } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import {
  HomeScreen,
  CameraScreen,
  ProcessingScreen,
  ResultScreen,
  AuditarModeloScreen,
  TestModeScreen,
  HistoryScreen,
  AboutScreen,
} from '@screens';
import { RootStackParamList } from './types';
import { COLORS } from '@utils/constants';

const Stack = createNativeStackNavigator<RootStackParamList>();
const Tab = createBottomTabNavigator<RootStackParamList>();

function AnalysisNavigator() {
  return (
    <Stack.Navigator
      initialRouteName="Home"
      screenOptions={{
        headerShown: false,
        cardStyle: { backgroundColor: COLORS.BACKGROUND },
        animationEnabled: true,
      }}
    >
      <Stack.Screen name="Home"          component={HomeScreen}          options={{ title: 'AgroVision' }} />
      <Stack.Screen name="Camera"        component={CameraScreen}        options={{ title: 'Capturar Imagem' }} />
      <Stack.Screen name="Processing"    component={ProcessingScreen}    options={{ title: 'Processando', gestureEnabled: false, animationEnabled: false }} />
      <Stack.Screen name="Result"        component={ResultScreen}        options={{ title: 'Resultado' }} />
      <Stack.Screen name="AuditarModelo" component={AuditarModeloScreen} options={{ title: 'Auditar Modelo' }} />
      <Stack.Screen name="TestMode"      component={TestModeScreen}      options={{ title: 'Modo Científico (lote)' }} />
    </Stack.Navigator>
  );
}

function HistoryNavigator() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false, cardStyle: { backgroundColor: COLORS.BACKGROUND } }}>
      <Stack.Screen name="History" component={HistoryScreen} />
    </Stack.Navigator>
  );
}

function AboutNavigator() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false, cardStyle: { backgroundColor: COLORS.BACKGROUND } }}>
      <Stack.Screen name="About" component={AboutScreen} />
    </Stack.Navigator>
  );
}

export function RootNavigator() {
  return (
    <NavigationContainer>
      <Tab.Navigator
        screenOptions={{
          headerShown: false,
          tabBarActiveTintColor: COLORS.PRIMARY,
          tabBarInactiveTintColor: COLORS.TEXT_SECONDARY,
          tabBarStyle: {
            backgroundColor: COLORS.BACKGROUND,
            borderTopColor: COLORS.BORDER,
            borderTopWidth: 1,
          },
        }}
      >
        <Tab.Screen
          name="AnalysisTab"
          component={AnalysisNavigator}
          options={{
            title: 'Análise',
            tabBarLabel: 'Análise',
            tabBarIcon: ({ color }) => <Text style={{ color, fontSize: 20 }}>🌽</Text>,
          }}
          listeners={({ navigation }) => ({
            tabPress: (e) => {
              e.preventDefault();
              navigation.navigate('Home');
            },
          })}
        />

        <Tab.Screen
          name="HistoryTab"
          component={HistoryNavigator}
          options={{
            title: 'Histórico',
            tabBarLabel: 'Histórico',
            tabBarIcon: ({ color }) => <Text style={{ color, fontSize: 20 }}>📋</Text>,
          }}
        />

        <Tab.Screen
          name="AboutTab"
          component={AboutNavigator}
          options={{
            title: 'Sobre',
            tabBarLabel: 'Sobre',
            tabBarIcon: ({ color }) => <Text style={{ color, fontSize: 20 }}>ℹ️</Text>,
          }}
        />
      </Tab.Navigator>
    </NavigationContainer>
  );
}
