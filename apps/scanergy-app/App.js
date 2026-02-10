import { StatusBar } from 'expo-status-bar';
import { StyleSheet, View } from 'react-native';
import { PaperProvider, MD3LightTheme, Button, Text } from 'react-native-paper';

export default function App() {
  const theme = {
    ...MD3LightTheme,
    colors: {
      ...MD3LightTheme.colors,
      primary: '#2962ff',
      secondary: '#00bfa5',
    },
  };

  return (
    <PaperProvider theme={theme}>
      <View style={styles.container}>
        <Text variant="headlineSmall">Scanergy</Text>
        <Text style={styles.subtitle}>Material design baseline with react-native-paper</Text>
        <Button mode="contained" onPress={() => {}}>
          Get Started
        </Button>
        <StatusBar style="auto" />
      </View>
    </PaperProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fafafa',
    alignItems: 'center',
    justifyContent: 'center',
  },
  subtitle: {
    marginVertical: 12,
  },
});
