import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { SectionHeader } from ".";

const meta: Meta<typeof SectionHeader> = {
  title: "Molecules/SectionHeader",
  component: SectionHeader,
  parameters: { layout: "padded" },
  tags: ["autodocs"],
  decorators: [
    (Story) => (
      <div style={{ width: "240px", background: "var(--color-bg-subtle)", padding: "8px", borderRadius: "8px" }}>
        <Story />
      </div>
    ),
  ],
};
export default meta;

type Story = StoryObj<typeof SectionHeader>;

export const Default: Story = {
  render: () => {
    const [collapsed, setCollapsed] = useState(false);
    return (
      <SectionHeader
        title="Szenen"
        count={8}
        isCollapsed={collapsed}
        onToggle={() => setCollapsed((c) => !c)}
        onAdd={() => alert("Szene hinzufügen")}
      />
    );
  },
};

export const Collapsed: Story = {
  render: () => {
    const [collapsed, setCollapsed] = useState(true);
    return (
      <SectionHeader
        title="Akteure"
        count={3}
        isCollapsed={collapsed}
        onToggle={() => setCollapsed((c) => !c)}
      />
    );
  },
};

export const Static: Story = {
  render: () => (
    <SectionHeader
      title="Einstellungen"
      isCollapsible={false}
      onToggle={() => {}}
    />
  ),
};

export const NoCount: Story = {
  render: () => {
    const [collapsed, setCollapsed] = useState(false);
    return (
      <SectionHeader
        title="Kapitel"
        isCollapsed={collapsed}
        onToggle={() => setCollapsed((c) => !c)}
        onAdd={() => {}}
      />
    );
  },
};

/** Simulates a full sidebar panel with multiple section headers. */
export const SidebarSimulation: Story = {
  render: () => {
    const [openSection, setOpenSection] = useState<string | null>("scenes");
    const toggle = (key: string) =>
      setOpenSection((cur) => (cur === key ? null : key));

    return (
      <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
        {[
          { key: "scenes", label: "Szenen", count: 12 },
          { key: "actors", label: "Akteure", count: 5 },
          { key: "themes", label: "Themen", count: 3 },
        ].map(({ key, label, count }) => (
          <SectionHeader
            key={key}
            title={label}
            count={count}
            isCollapsed={openSection !== key}
            onToggle={() => toggle(key)}
            onAdd={() => alert(`${label} hinzufügen`)}
          />
        ))}
      </div>
    );
  },
};
