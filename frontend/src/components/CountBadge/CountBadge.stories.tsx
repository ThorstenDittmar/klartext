import type { Meta, StoryObj } from "@storybook/react";
import { CountBadge } from ".";

const meta: Meta<typeof CountBadge> = {
  title: "Atoms/CountBadge",
  component: CountBadge,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
};
export default meta;

type Story = StoryObj<typeof CountBadge>;

export const Default: Story = { args: { count: 5 } };
export const LargeCount: Story = { args: { count: 42 } };
export const MaxExceeded: Story = { args: { count: 150 } };
export const ZeroVisible: Story = { args: { count: 0, hideWhenZero: false } };
export const Dot: Story = { args: { count: 1, variant: "dot" } };

export const InContext: Story = {
  render: () => (
    <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "13px", color: "var(--color-text-primary)" }}>
        <span>Szenen</span>
        <CountBadge count={12} aria-label="12 Szenen" />
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "13px", color: "var(--color-text-primary)" }}>
        <span>Akteure</span>
        <CountBadge count={5} aria-label="5 Akteure" />
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "13px", color: "var(--color-text-primary)" }}>
        <span>Kommentare</span>
        <CountBadge count={130} aria-label="Mehr als 99 Kommentare" />
      </div>
    </div>
  ),
};
