<?xml version="1.0" ?>
<!--  Written by: Chris A. Poblete -->
<!--
##############################################################################
# Copyright (c) 2011, Dell Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Dell, Inc. nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL Dell, Inc. BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
##############################################################################
-->
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:s="http://www.w3.org/2003/05/soap-envelope"
    xmlns:cim="http://schemas.dmtf.org/wbem/wscim/1/common"
    xmlns:wsman="http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd">
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

