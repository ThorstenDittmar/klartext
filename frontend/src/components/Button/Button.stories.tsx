import type { Meta, StoryObj } from "@storybook/react";
import { Button } from ".";

const meta: Meta<typeof Button> = {
  title: "Atoms/Button",
  component: Button,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  argTypes: {
    variant: {
      control: "select",
      options: ["primary", "secondary", "ghost", "nav-item"],
    },
  },
};
export default meta;

type Story = StoryObj<typeof Button>;

export const Primary: Story = {
  args: { children: "Speichern", variant: "primary" },
};

export const Secondary: Story = {
  args: { children: "Abbrechen", variant: "secondary" },
};

export const Ghost: Story = {
  args: { children: "← Zurück", variant: "ghost" },
};

export const NavItem: Story = {
  args: { children: "Szenenplan", variant: "nav-item" },
};

export const NavItemActive: Story = {
  args: { children: "Szenenplan", variant: "nav-item", isActive: true },
};

export const Loading: Story = {
  args: { children: "Speichern", variant: "primary", isLoading: true },
};

export const Disabled: Story = {
  args: { children: "Nicht verfügbar", variant: "primary", disabled: true },
};

export const FullWidth: Story = {
  args: { children: "Anlegen", variant: "primary", fullWidth: true },
  parameters: { layout: "padded" },
};

/** All variants side-by-side for quick design review. */
export const AllVariants: Story = {
  render: () => (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
        <Button variant="primary">Primary</Button>
        <Button variant="secondary">Secondary</Button>
        <Button variant="ghost">← Ghost</Button>
      </div>
      <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
        <Button variant="primary" isLoading>Loading</Button>
        <Button variant="secondary" isLoading>Loading</Button>
        <Button variant="ghost" disabled>Disabled</Button>
      </div>
      <div
        style={{
          width: "220px",
          display: "flex",
          flexDirection: "column",
          gap: "4px",
          background: "var(--color-bg-subtle)",
          padding: "8px",
          borderRadius: "8px",
        }}
      >
        <Button variant="nav-item">Meine Werke</Button>
        <Button variant="nav-item" isActive>Szenenplan</Button>
        <Button variant="nav-item">Akteure</Button>
        <Button variant="nav-item">Analyse</Button>
      </div>
    </div>
  ),
};
