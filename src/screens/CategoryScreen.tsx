import React from 'react';
import { View, FlatList, StyleSheet, TouchableOpacity, Text } from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { COLORS, UI } from '@utils/constants';
import { RootStackParamList } from '@navigation/types';
import { Category } from '@models/institutional';

type CategoryScreenProps = NativeStackScreenProps<RootStackParamList, 'InstitutionalCategory'>;

export const CategoryScreen: React.FC<CategoryScreenProps> = ({ route, navigation }) => {
  const { category } = route.params;

  React.useEffect(() => {
    if (category?.name) {
      navigation.setOptions({
        headerTitle: category.name,
      });
    }
  }, [navigation, category?.name]);

  if (!category || !category.items || category.items.length === 0) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>Categoria não encontrada</Text>
        </View>
      </SafeAreaView>
    );
  }

  const handleItemPress = (item: typeof category.items[0]) => {
    navigation.navigate('InstitutionalArticle', {
      item,
      categoryName: category.name,
    });
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.icon}>{category.icon}</Text>
        <Text style={styles.title}>{category.name}</Text>
      </View>

      {/* Lista de Itens */}
      <FlatList
        data={category.items}
        keyExtractor={(item) => item.id}
        renderItem={({ item, index }) => (
          <TouchableOpacity
            style={[styles.itemCard, index === category.items.length - 1 && styles.lastItem]}
            onPress={() => handleItemPress(item)}
            activeOpacity={0.7}
          >
            <View style={styles.itemLeft}>
              <View style={styles.itemNumber}>
                <Text style={styles.numberText}>{index + 1}</Text>
              </View>
              <Text style={styles.itemName}>{item.name}</Text>
            </View>
            <Text style={styles.chevron}>›</Text>
          </TouchableOpacity>
        )}
        contentContainerStyle={styles.listContent}
        scrollEnabled={true}
        showsVerticalScrollIndicator={false}
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.BACKGROUND,
  },
  header: {
    backgroundColor: COLORS.PRIMARY,
    paddingHorizontal: UI.spacing.lg,
    paddingVertical: UI.spacing.lg,
    flexDirection: 'row',
    alignItems: 'center',
    gap: UI.spacing.md,
  },
  icon: {
    fontSize: 36,
  },
  title: {
    fontSize: 22,
    fontWeight: '700',
    color: COLORS.WHITE,
    flex: 1,
  },
  listContent: {
    padding: UI.spacing.lg,
    paddingBottom: UI.spacing.xl,
  },
  itemCard: {
    backgroundColor: COLORS.WHITE,
    marginBottom: UI.spacing.md,
    borderRadius: UI.spacing.md,
    padding: UI.spacing.md,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 4,
    shadowOffset: { width: 0, height: 1 },
    elevation: 2,
  },
  lastItem: {
    marginBottom: 0,
  },
  itemLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    gap: UI.spacing.md,
  },
  itemNumber: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: COLORS.PRIMARY,
    justifyContent: 'center',
    alignItems: 'center',
  },
  numberText: {
    color: COLORS.WHITE,
    fontWeight: '600',
    fontSize: 14,
  },
  itemName: {
    fontSize: 16,
    color: COLORS.DARK_GRAY,
    fontWeight: '500',
    flex: 1,
  },
  chevron: {
    fontSize: 24,
    color: COLORS.SECONDARY,
    fontWeight: '300',
  },
});
