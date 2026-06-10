import type { Meta, StoryObj } from "@storybook/react";
import { Badge } from ".";

const meta: Meta<typeof Badge> = {
  title: "Atoms/Badge",
  component: Badge,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  argTypes: {
    colorKey: {
      control: "select",
      options: ["default", "green", "amber", "red", "blue", "teal"],
    },
    variant: {
      control: "select",
      options: ["status", "category", "outline"],
    },
  },
};
export default meta;

type Story = StoryObj<typeof Badge>;

export const Default: Story = {
  args: { label: "Entwurf", colorKey: "default" },
};

export const Green: Story = {
  args: { label: "Abgeschlossen", colorKey: "green" },
};

export const Amber: Story = {
  args: { label: "Ausstehend", colorKey: "amber" },
};

export const Red: Story = {
  args: { label: "Fehler", colorKey: "red" },
};

export const Blue: Story = {
  args: { label: "Info", colorKey: "blue" },
};

export const Teal: Story = {
  args: { label: "Kernkonzept", colorKey: "teal" },
};

export const Outline: Story = {
  args: { label: "Kategorie", colorKey: "blue", variant: "outline" },
};

/** All colour keys and variants side-by-side for design review. */
export const AllColors: Story = {
  render: () => (
    <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
      <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", alignItems: "center" }}>
        <span style={{ fontSize: "11px", color: "var(--color-text-tertiary)", width: "64px" }}>Status</span>
        <Badge label="Standard" colorKey="default" />
        <Badge label="Erfolg" colorKey="green" />
        <Badge label="Warnung" colorKey="amber" />
        <Badge label="Fehler" colorKey="red" />
        <Badge label="Info" colorKey="blue" />
        <Badge label="Kernkonzept" colorKey="teal" />
      </div>
      <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", alignItems: "center" }}>
        <span style={{ fontSize: "11px", color: "var(--color-text-tertiary)", width: "64px" }}>Outline</span>
        <Badge label="Standard" colorKey="default" variant="outline" />
        <Badge label="Erfolg" colorKey="green" variant="outline" />
        <Badge label="Warnung" colorKey="amber" variant="outline" />
        <Badge label="Fehler" colorKey="red" variant="outline" />
        <Badge label="Info" colorKey="blue" variant="outline" />
        <Badge label="Kernkonzept" colorKey="teal" variant="outline" />
      </div>
    </div>
  ),
};
