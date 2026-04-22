import React from 'react';
import { View, ScrollView, StyleSheet, TouchableOpacity, Text, Dimensions } from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { INSTITUTIONAL_CATEGORIES } from '@data/institutionalData';
import { COLORS, UI } from '@utils/constants';
import { RootStackParamList } from '@navigation/types';

type InstitutionalScreenProps = NativeStackScreenProps<RootStackParamList, 'Institutional'>;

const { width } = Dimensions.get('window');
const cardWidth = (width - UI.spacing.lg * 2 - UI.spacing.md) / 2;

export const InstitutionalScreen: React.FC<InstitutionalScreenProps> = ({ navigation }) => {
  return (
    <SafeAreaView style={styles.container}>
      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>📚 Biblioteca Agronômica</Text>
          <Text style={styles.subtitle}>Aprenda sobre culturas, doenças, pragas e solos</Text>
        </View>

        {/* Grid de Categorias */}
        <View style={styles.grid}>
          {INSTITUTIONAL_CATEGORIES.map((category) => (
            <TouchableOpacity
              key={category.id}
              style={[styles.card, { width: cardWidth }]}
              onPress={() => navigation.navigate('InstitutionalCategory', { category })}
              activeOpacity={0.8}
            >
              <View style={styles.iconContainer}>
                <Text style={styles.icon}>{category.icon}</Text>
              </View>
              <Text style={styles.cardTitle}>{category.name}</Text>
              <Text style={styles.itemCount}>{category.items.length} tópicos</Text>
              <View style={styles.arrow}>
                <Text style={styles.arrowIcon}>→</Text>
              </View>
            </TouchableOpacity>
          ))}
        </View>

        {/* Footer Info */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>
            💡 Dica: Clique em qualquer categoria para explorar tópicos relacionados.
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.BACKGROUND,
  },
  header: {
    paddingHorizontal: UI.spacing.lg,
    paddingVertical: UI.spacing.lg,
    backgroundColor: COLORS.PRIMARY,
    borderBottomLeftRadius: UI.spacing.lg,
    borderBottomRightRadius: UI.spacing.lg,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: COLORS.WHITE,
    marginBottom: UI.spacing.sm,
  },
  subtitle: {
    fontSize: 14,
    color: COLORS.WHITE,
    opacity: 0.9,
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: UI.spacing.lg,
    paddingBottom: UI.spacing.xl,
    justifyContent: 'space-between',
    gap: UI.spacing.md,
  },
  card: {
    backgroundColor: COLORS.WHITE,
    borderRadius: UI.spacing.md,
    padding: UI.spacing.md,
    marginBottom: UI.spacing.sm,
    shadowColor: '#000',
    shadowOpacity: 0.08,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 2 },
    elevation: 3,
  },
  iconContainer: {
    width: 60,
    height: 60,
    borderRadius: 12,
    backgroundColor: COLORS.LIGHT_GRAY,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: UI.spacing.md,
  },
  icon: {
    fontSize: 32,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.DARK_GRAY,
    marginBottom: UI.spacing.xs,
  },
  itemCount: {
    fontSize: 12,
    color: COLORS.SECONDARY,
    fontWeight: '500',
    marginBottom: UI.spacing.md,
  },
  arrow: {
    alignSelf: 'flex-end',
  },
  arrowIcon: {
    fontSize: 20,
    color: COLORS.PRIMARY,
    fontWeight: '600',
  },
  footer: {
    marginHorizontal: UI.spacing.lg,
    marginVertical: UI.spacing.xl,
    padding: UI.spacing.md,
    backgroundColor: COLORS.LIGHT_GRAY,
    borderRadius: UI.spacing.md,
    borderLeftWidth: 4,
    borderLeftColor: COLORS.INFO,
  },
  footerText: {
    fontSize: 13,
    color: COLORS.DARK_GRAY,
    fontWeight: '500',
  },
});
