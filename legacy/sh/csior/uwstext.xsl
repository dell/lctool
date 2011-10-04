<?xml version="1.0" ?>
<!--  Written by: Chris A. Poblete -->
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:s="http://www.w3.org/2003/05/soap-envelope"
    xmlns:cim="http://schemas.dell.com/wbem/wscim/1/common"
    xmlns:wsman="http://schemas.dell.com/wbem/wsman/1/wsman.xsd">
  <xsl:output method="text"/>

  <xsl:param name="index">1</xsl:param>

  <xsl:template name="doIndent">
    <xsl:param name="counter2"/>
    <xsl:if test="$counter2 &gt; 0">
      <xsl:value-of select="'   '"/>
      <xsl:call-template name="doIndent">
        <xsl:with-param name="counter2" select="$counter2 - 1"/>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>

  <xsl:template match="/">
    <xsl:choose>
      <xsl:when test="//wsman:Items">
        <xsl:if test="count(//wsman:Items/*) = 0">
          <xsl:text>[EMPTY]&#xA;</xsl:text>
        </xsl:if>
        <xsl:apply-templates select="//wsman:Items/*">
          <xsl:with-param name="counter1" select="0"/>
          <xsl:with-param name="isitem" select="1"/>
        </xsl:apply-templates>
      </xsl:when>
      <xsl:otherwise>
        <xsl:if test="count(//s:Body/*) = 0">
          <xsl:text>[EMPTY]&#xA;</xsl:text>
        </xsl:if>
        <xsl:apply-templates select="//s:Body/*">
          <xsl:with-param name="counter1" select="0"/>
          <xsl:with-param name="isitem" select="0"/>
        </xsl:apply-templates>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="*[text()] | *[@xsi:nil]">
    <xsl:param name="counter1"/>
    <xsl:if test="name(preceding-sibling::node()[1]) != name()">
      <xsl:call-template name="doIndent">
        <xsl:with-param name="counter2" select="$counter1"/>
      </xsl:call-template>
      <xsl:if test="@cim:Key">
        <xsl:text>*</xsl:text>
      </xsl:if>
      <xsl:value-of select="local-name()"/>
      <xsl:if test="@Name">
        <xsl:value-of select="': '"/>
        <xsl:value-of select="@Name"/>
      </xsl:if>
      <xsl:value-of select="' = '"/>
    </xsl:if>
    <xsl:if test="name(preceding-sibling::node()[1]) = name()">
      <xsl:if test="@Name">
        <xsl:value-of select="@Name"/>
        <xsl:value-of select="' = '"/>
      </xsl:if>
    </xsl:if>
    <xsl:if test="not(@xsi:nil)">
      <xsl:value-of select="."/>
    </xsl:if>
    <xsl:if test="@xsi:nil">
      <xsl:value-of select="'[null]'"/>
    </xsl:if>
    <xsl:if test="name(following-sibling::node()[1]) = name()">, </xsl:if>
    <xsl:if test="name(following-sibling::node()[1]) != name()">
      <xsl:value-of select="'&#xA;'"/>
    </xsl:if>
  </xsl:template>

  <xsl:template match="*">
    <xsl:param name="counter1"/>
    <xsl:param name="isitem" />
    <xsl:call-template name="doIndent">
      <xsl:with-param name="counter2" select="$counter1"/>
    </xsl:call-template>
    <xsl:if test="string-length() &gt; 0">
      <xsl:if test="$isitem = 1">
        <xsl:value-of select="'('"/>
        <xsl:value-of select="position()"/>
        <xsl:value-of select="') '"/>
      </xsl:if>
    </xsl:if>
    <xsl:value-of select="local-name()"/>
    <xsl:value-of select="'&#xA;'"/>
    <xsl:apply-templates>
      <xsl:with-param name="counter1" select="$counter1 + 1"/>
      <xsl:with-param name="isitem" select="0"/>
    </xsl:apply-templates>
    <xsl:if test="$counter1 = 0">
      <xsl:value-of select="'&#xA;'"/>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>

