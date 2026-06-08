import type { Meta, StoryObj } from "@storybook/react";
import { EmptyState } from ".";

const meta: Meta<typeof EmptyState> = {
  title: "Molecules/EmptyState",
  component: EmptyState,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
};
export default meta;

type Story = StoryObj<typeof EmptyState>;

export const Default: Story = {
  args: {
    title: "Keine Szenen vorhanden",
    subtitle: "Leg eine erste Szene an um mit dem Szenenplan zu beginnen.",
    actionLabel: "Szene erstellen",
    onAction: () => alert("Szene erstellen"),
  },
};

export const TitleOnly: Story = {
  args: { title: "Noch keine Einträge." },
};

export const SearchNoResults: Story = {
  args: {
    title: "Keine Treffer",
    subtitle: "Deine Suche hat keine Ergebnisse geliefert. Passe den Suchbegriff an.",
    icon: "🔍",
  },
};

export const ErrorState: Story = {
  args: {
    title: "Laden fehlgeschlagen",
    subtitle: "Die Daten konnten nicht geladen werden. Bitte versuche es erneut.",
    actionLabel: "Erneut versuchen",
    onAction: () => alert("Retry"),
    icon: "⚠",
  },
};

export const WithIcon: Story = {
  args: {
    title: "Keine Narrative",
    subtitle: "Erstelle dein erstes Narrativ um loszulegen.",
    actionLabel: "Narrativ anlegen",
    onAction: () => {},
    icon: "✦",
  },
};

/** Shows how EmptyState looks inside a panel with a border. */
export const InPanel: Story = {
  render: () => (
    <div
      style={{
        width: "360px",
        border: "1px solid var(--color-border)",
        borderRadius: "8px",  // radius.lg
        background: "var(--color-bg)",
      }}
    >
      <EmptyState
        title="Keine Akteure"
        subtitle="Füge Akteure hinzu um Szenen zuzuordnen."
        actionLabel="Akteur hinzufügen"
        onAction={() => {}}
      />
    </div>
  ),
};
