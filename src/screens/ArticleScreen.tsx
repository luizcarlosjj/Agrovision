import React from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  Image,
  Linking,
  ActivityIndicator,
} from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { institutionalService } from '@services/api/institutionalService';
import { COLORS, UI } from '@utils/constants';
import { RootStackParamList } from '@navigation/types';
import { WikiArticle } from '@models/institutional';

type ArticleScreenProps = NativeStackScreenProps<RootStackParamList, 'InstitutionalArticle'>;

export const ArticleScreen: React.FC<ArticleScreenProps> = ({ route, navigation }) => {
  const { item, categoryName } = route.params;
  const [article, setArticle] = React.useState<WikiArticle | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (item?.name) {
      navigation.setOptions({
        headerTitle: item.name,
      });
    }
    if (item?.searchTerm) {
      loadArticle();
    }
  }, [item?.name, item?.searchTerm, navigation]);

  const loadArticle = async () => {
    if (!item?.searchTerm) {
      setError('Item inválido');
      setLoading(false);
      return;
    }
    try {
      setLoading(true);
      setError(null);
      const result = await institutionalService.fetchWikiSummary(item.searchTerm);
      setArticle(result);
    } catch (err) {
      setError('Erro ao carregar artigo');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.centerContent}>
          <ActivityIndicator size="large" color={COLORS.PRIMARY} />
          <Text style={styles.loadingText}>Carregando artigo...</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (error || !article) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.errorContainer}>
          <Text style={styles.errorIcon}>⚠️</Text>
          <Text style={styles.errorText}>{error || 'Conteúdo não disponível'}</Text>
          <TouchableOpacity style={styles.retryButton} onPress={loadArticle}>
            <Text style={styles.retryButtonText}>Tentar Novamente</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Hero Image */}
        {article.imageUrl ? (
          <Image source={{ uri: article.imageUrl }} style={styles.heroImage} />
        ) : (
          <View style={styles.noImage}>
            <Text style={styles.noImageIcon}>🖼️</Text>
            <Text style={styles.noImageText}>Sem imagem disponível</Text>
          </View>
        )}

        {/* Content */}
        <View style={styles.content}>
          {/* Badge */}
          <View style={styles.badgeContainer}>
            <View style={styles.badge}>
              <Text style={styles.badgeText}>{categoryName}</Text>
            </View>
          </View>

          {/* Title */}
          <Text style={styles.title}>{article.title}</Text>

          {/* Summary */}
          <Text style={styles.summary}>{article.summary}</Text>

          {/* Read More Button */}
          <TouchableOpacity
            style={styles.button}
            onPress={() => Linking.openURL(article.pageUrl)}
            activeOpacity={0.8}
          >
            <Text style={styles.buttonIcon}>📖</Text>
            <Text style={styles.buttonText}>Ler Artigo Completo</Text>
          </TouchableOpacity>

          {/* Footer */}
          <View style={styles.footer}>
            <View style={styles.footerRow}>
              <Text style={styles.footerLabel}>📅 Última atualização:</Text>
              <Text style={styles.footerValue}>{article.lastModified}</Text>
            </View>
            <View style={styles.footerRow}>
              <Text style={styles.footerLabel}>📚 Fonte:</Text>
              <Text style={styles.footerValue}>Wikipedia</Text>
            </View>
          </View>
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
  centerContent: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: UI.spacing.md,
    fontSize: 16,
    color: COLORS.DARK_GRAY,
  },
  heroImage: {
    width: '100%',
    height: 250,
    backgroundColor: COLORS.LIGHT_GRAY,
  },
  noImage: {
    width: '100%',
    height: 200,
    backgroundColor: COLORS.LIGHT_GRAY,
    justifyContent: 'center',
    alignItems: 'center',
  },
  noImageIcon: {
    fontSize: 48,
    marginBottom: UI.spacing.sm,
  },
  noImageText: {
    fontSize: 14,
    color: COLORS.TEXT_SECONDARY,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: UI.spacing.lg,
  },
  errorIcon: {
    fontSize: 48,
    marginBottom: UI.spacing.md,
  },
  errorText: {
    fontSize: 16,
    color: COLORS.DARK_GRAY,
    textAlign: 'center',
    marginBottom: UI.spacing.lg,
  },
  retryButton: {
    backgroundColor: COLORS.PRIMARY,
    paddingHorizontal: UI.spacing.lg,
    paddingVertical: UI.spacing.md,
    borderRadius: UI.spacing.md,
  },
  retryButtonText: {
    color: COLORS.WHITE,
    fontSize: 16,
    fontWeight: '600',
  },
  content: {
    padding: UI.spacing.lg,
  },
  badgeContainer: {
    flexDirection: 'row',
    marginBottom: UI.spacing.md,
  },
  badge: {
    backgroundColor: COLORS.SECONDARY,
    paddingHorizontal: UI.spacing.md,
    paddingVertical: UI.spacing.sm,
    borderRadius: UI.spacing.md,
  },
  badgeText: {
    color: COLORS.WHITE,
    fontSize: 12,
    fontWeight: '600',
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: COLORS.DARK_GRAY,
    marginBottom: UI.spacing.lg,
    lineHeight: 32,
  },
  summary: {
    fontSize: 15,
    lineHeight: 24,
    color: COLORS.TEXT_PRIMARY,
    marginBottom: UI.spacing.xl,
  },
  button: {
    backgroundColor: COLORS.PRIMARY,
    paddingHorizontal: UI.spacing.lg,
    paddingVertical: UI.spacing.md,
    borderRadius: UI.spacing.md,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: UI.spacing.xl,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 4,
    shadowOffset: { width: 0, height: 2 },
    elevation: 3,
  },
  buttonIcon: {
    fontSize: 20,
    marginRight: UI.spacing.sm,
  },
  buttonText: {
    color: COLORS.WHITE,
    fontSize: 16,
    fontWeight: '600',
  },
  footer: {
    backgroundColor: COLORS.LIGHT_GRAY,
    padding: UI.spacing.md,
    borderRadius: UI.spacing.md,
    borderLeftWidth: 4,
    borderLeftColor: COLORS.INFO,
  },
  footerRow: {
    flexDirection: 'row',
    marginBottom: UI.spacing.sm,
    alignItems: 'center',
  },
  footerLabel: {
    fontSize: 12,
    color: COLORS.TEXT_SECONDARY,
    fontWeight: '500',
    marginRight: UI.spacing.sm,
  },
  footerValue: {
    fontSize: 12,
    color: COLORS.DARK_GRAY,
    fontWeight: '600',
  },
});
